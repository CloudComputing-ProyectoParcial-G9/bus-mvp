"""
AWS Athena service for executing SQL queries
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class AthenaService:
    """AWS Athena service for analytics queries"""
    
    def __init__(self):
        self.athena_client = None
        self.s3_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AWS clients"""
        try:
            session_kwargs = {
                'region_name': settings.aws_region
            }
            
            # Add credentials if provided
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                session_kwargs.update({
                    'aws_access_key_id': settings.aws_access_key_id,
                    'aws_secret_access_key': settings.aws_secret_access_key
                })
            elif settings.aws_profile:
                session = boto3.Session(profile_name=settings.aws_profile)
                self.athena_client = session.client('athena', region_name=settings.aws_region)
                self.s3_client = session.client('s3', region_name=settings.aws_region)
                return
            
            self.athena_client = boto3.client('athena', **session_kwargs)
            self.s3_client = boto3.client('s3', **session_kwargs)
            
        except Exception as e:
            logger.error("Failed to initialize AWS clients", error=str(e))
            raise
    
    async def execute_query(self, sql_query: str, max_results: int = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Execute a query in Athena and return results
        
        Args:
            sql_query: SQL query to execute
            max_results: Maximum number of results to return
            
        Returns:
            Tuple of (execution_id, results_list)
        """
        try:
            start_time = time.time()
            
            # Start query execution
            execution_id = await self._start_query_execution(sql_query)
            
            # Wait for completion and get results
            results = await self._get_query_results(
                execution_id, 
                max_results or settings.aws_athena_max_results
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            logger.info(
                "Query executed successfully",
                execution_id=execution_id,
                execution_time_ms=execution_time,
                result_count=len(results)
            )
            
            return execution_id, results
            
        except Exception as e:
            logger.error("Failed to execute query", error=str(e), query=sql_query[:100])
            raise
    
    async def _start_query_execution(self, sql_query: str) -> str:
        """Start query execution in Athena"""
        try:
            response = self.athena_client.start_query_execution(
                QueryString=sql_query,
                QueryExecutionContext={'Database': settings.aws_glue_catalog_database},
                ResultConfiguration={'OutputLocation': settings.query_output_path},
                WorkGroup=settings.aws_athena_workgroup
            )
            
            execution_id = response['QueryExecutionId']
            logger.info("Query execution started", execution_id=execution_id)
            
            return execution_id
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error("Athena query execution failed", error_code=error_code, error_message=error_message)
            raise Exception(f"Athena error: {error_code} - {error_message}")
    
    async def _get_query_results(self, execution_id: str, max_results: int) -> List[Dict[str, Any]]:
        """Get query results from Athena"""
        try:
            # Wait for query to complete
            await self._wait_for_query_completion(execution_id)
            
            # Get results
            paginator = self.athena_client.get_paginator('get_query_results')
            page_iterator = paginator.paginate(
                QueryExecutionId=execution_id,
                MaxItems=max_results,
                PaginationConfig={'PageSize': 1000}
            )
            
            results = []
            column_names = None
            
            for page in page_iterator:
                if column_names is None:
                    # Extract column names from first page
                    column_info = page['ResultSet']['ResultSetMetadata']['ColumnInfo']
                    column_names = [col['Name'] for col in column_info]
                    
                    # Skip header row if it exists
                    rows = page['ResultSet']['Rows'][1:] if page['ResultSet']['Rows'] else []
                else:
                    rows = page['ResultSet']['Rows']
                
                # Convert rows to dictionaries
                for row in rows:
                    row_data = {}
                    for i, col_name in enumerate(column_names):
                        value = row['Data'][i].get('VarCharValue', '')
                        # Try to convert to appropriate type
                        row_data[col_name] = self._convert_value(value)
                    results.append(row_data)
            
            return results
            
        except Exception as e:
            logger.error("Failed to get query results", execution_id=execution_id, error=str(e))
            raise
    
    async def _wait_for_query_completion(self, execution_id: str):
        """Wait for query to complete with timeout"""
        timeout = settings.aws_athena_query_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.athena_client.get_query_execution(QueryExecutionId=execution_id)
                status = response['QueryExecution']['Status']['State']
                
                if status == 'SUCCEEDED':
                    return
                elif status in ['FAILED', 'CANCELLED']:
                    reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                    raise Exception(f"Query {status.lower()}: {reason}")
                
                # Wait before checking again
                await asyncio.sleep(1)
                
            except ClientError as e:
                logger.error("Error checking query status", execution_id=execution_id, error=str(e))
                raise
        
        # Timeout reached
        raise Exception(f"Query timeout after {timeout} seconds")
    
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate Python type"""
        if not value or value == '':
            return None
        
        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            # Try boolean
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            
            # Return as string
            return value
    
    async def get_table_metadata(self, table_name: str) -> Dict[str, Any]:
        """Get metadata for a table from Glue catalog"""
        try:
            glue_client = boto3.client('glue', region_name=settings.aws_region)
            response = glue_client.get_table(
                DatabaseName=settings.aws_glue_catalog_database,
                Name=table_name
            )
            
            return {
                'name': response['Table']['Name'],
                'columns': [
                    {'name': col['Name'], 'type': col['Type']}
                    for col in response['Table']['StorageDescriptor']['Columns']
                ],
                'location': response['Table']['StorageDescriptor']['Location'],
                'partitions': response['Table'].get('PartitionKeys', [])
            }
            
        except Exception as e:
            logger.error("Failed to get table metadata", table=table_name, error=str(e))
            raise
    
    async def health_check(self) -> Dict[str, str]:
        """Check health of Athena service"""
        try:
            # Simple query to check if service is accessible
            response = self.athena_client.list_work_groups(MaxResults=1)
            return {"status": "healthy", "message": "Athena service accessible"}
            
        except NoCredentialsError:
            return {"status": "unhealthy", "message": "AWS credentials not configured"}
        except ClientError as e:
            return {"status": "unhealthy", "message": f"AWS error: {e.response['Error']['Code']}"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Unknown error: {str(e)}"}
