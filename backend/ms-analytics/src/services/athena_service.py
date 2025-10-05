import boto3
import time
from typing import List, Dict, Any
from loguru import logger
from src.config import Settings
from src.core.exceptions import AthenaQueryException, AthenaTimeoutException

class AthenaService:
    """
    Servicio para ejecutar queries en AWS Athena
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = boto3.client(
            'athena',
            region_name=settings.aws_default_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            aws_session_token=settings.aws_session_token if settings.aws_session_token else None
        )
        self.database = settings.glue_database
        self.output_location = settings.athena_output_location
        self.query_timeout = settings.athena_query_timeout
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Ejecuta una query en Athena y retorna los resultados
        
        Args:
            query: Query SQL a ejecutar
            
        Returns:
            Lista de diccionarios con los resultados
            
        Raises:
            AthenaQueryException: Si falla la query
            AthenaTimeoutException: Si excede el timeout
        """
        try:
            logger.info(f"Executing Athena query: {query[:100]}...")
            
            # Iniciar ejecución de query
            response = self.client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': self.database},
                ResultConfiguration={'OutputLocation': self.output_location}
            )
            
            query_execution_id = response['QueryExecutionId']
            logger.info(f"Query execution ID: {query_execution_id}")
            
            # Esperar resultados
            results = await self._wait_for_query_completion(query_execution_id)
            
            return results
            
        except AthenaTimeoutException:
            raise
        except Exception as e:
            logger.error(f"Error executing Athena query: {str(e)}")
            raise AthenaQueryException(str(e))
    
    async def _wait_for_query_completion(self, query_execution_id: str) -> List[Dict[str, Any]]:
        """
        Espera a que la query complete y retorna resultados
        
        Args:
            query_execution_id: ID de ejecución de query
            
        Returns:
            Resultados parseados
        """
        start_time = time.time()
        
        while True:
            # Verificar timeout
            if time.time() - start_time > self.query_timeout:
                raise AthenaTimeoutException(f"Query exceeded timeout of {self.query_timeout}s")
            
            # Obtener estado
            response = self.client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            
            status = response['QueryExecution']['Status']['State']
            
            if status == 'SUCCEEDED':
                logger.info("Query succeeded")
                return await self._get_query_results(query_execution_id)
            
            elif status in ['FAILED', 'CANCELLED']:
                reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                logger.error(f"Query {status}: {reason}")
                raise AthenaQueryException(f"Query {status}: {reason}")
            
            # Esperar antes de siguiente check
            time.sleep(1)
    
    async def _get_query_results(self, query_execution_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene y parsea resultados de query
        
        Args:
            query_execution_id: ID de ejecución
            
        Returns:
            Lista de diccionarios con resultados
        """
        results = []
        next_token = None
        
        while True:
            # Obtener página de resultados
            params = {'QueryExecutionId': query_execution_id, 'MaxResults': 1000}
            if next_token:
                params['NextToken'] = next_token
            
            response = self.client.get_query_results(**params)
            
            # Parsear resultados
            if not results:  # Primera página
                # Extraer nombres de columnas
                columns = [col['Name'] for col in response['ResultSet']['ResultSetMetadata']['ColumnInfo']]
                
                # Saltar header row y parsear datos
                for row in response['ResultSet']['Rows'][1:]:
                    values = [field.get('VarCharValue', None) for field in row['Data']]
                    results.append(dict(zip(columns, values)))
            else:
                # Páginas subsecuentes
                for row in response['ResultSet']['Rows']:
                    values = [field.get('VarCharValue', None) for field in row['Data']]
                    results.append(dict(zip(columns, values)))
            
            # Verificar si hay más páginas
            next_token = response.get('NextToken')
            if not next_token:
                break
        
        logger.info(f"Retrieved {len(results)} rows")
        return results
    
    async def test_connection(self) -> bool:
        """
        Prueba conexión con Athena ejecutando query simple
        
        Returns:
            True si conexión exitosa
        """
        try:
            query = f"SHOW TABLES IN {self.database}"
            await self.execute_query(query)
            return True
        except Exception as e:
            logger.error(f"Athena connection test failed: {str(e)}")
            return False
