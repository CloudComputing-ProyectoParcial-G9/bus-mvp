"""
AWS helper utilities
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Any, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class AWSHealthChecker:
    """Helper class to check AWS service health"""
    
    @staticmethod
    async def check_s3_health() -> Dict[str, str]:
        """Check S3 service health"""
        try:
            s3_client = boto3.client('s3', region_name=settings.aws_region)
            # Try to list buckets (requires minimal permissions)
            s3_client.list_buckets()
            return {"status": "healthy", "message": "S3 accessible"}
        
        except NoCredentialsError:
            return {"status": "unhealthy", "message": "No AWS credentials"}
        except ClientError as e:
            error_code = e.response['Error']['Code']
            return {"status": "unhealthy", "message": f"S3 error: {error_code}"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"S3 unknown error: {str(e)}"}
    
    @staticmethod
    async def check_glue_health() -> Dict[str, str]:
        """Check Glue service health"""
        try:
            glue_client = boto3.client('glue', region_name=settings.aws_region)
            # Try to get database info
            glue_client.get_database(Name=settings.aws_glue_catalog_database)
            return {"status": "healthy", "message": "Glue catalog accessible"}
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityNotFoundException':
                return {"status": "degraded", "message": f"Database {settings.aws_glue_catalog_database} not found"}
            return {"status": "unhealthy", "message": f"Glue error: {error_code}"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Glue unknown error: {str(e)}"}
    
    @staticmethod
    async def check_athena_health() -> Dict[str, str]:
        """Check Athena service health"""
        try:
            athena_client = boto3.client('athena', region_name=settings.aws_region)
            # Try to list work groups
            athena_client.list_work_groups(MaxResults=1)
            return {"status": "healthy", "message": "Athena accessible"}
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            return {"status": "unhealthy", "message": f"Athena error: {error_code}"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Athena unknown error: {str(e)}"}


def get_aws_session() -> Optional[boto3.Session]:
    """Get configured AWS session"""
    try:
        if settings.aws_profile:
            return boto3.Session(profile_name=settings.aws_profile)
        elif settings.aws_access_key_id and settings.aws_secret_access_key:
            return boto3.Session(
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
        else:
            # Use default credentials (IAM role, environment variables, etc.)
            return boto3.Session()
    
    except Exception as e:
        logger.error("Failed to create AWS session", error=str(e))
        return None


def format_s3_path(bucket: str, key: str) -> str:
    """Format S3 path with proper s3:// prefix"""
    return f"s3://{bucket}/{key.lstrip('/')}"


def parse_s3_path(s3_path: str) -> Dict[str, str]:
    """Parse S3 path into bucket and key components"""
    if not s3_path.startswith('s3://'):
        raise ValueError("Invalid S3 path format")
    
    path_parts = s3_path[5:].split('/', 1)
    bucket = path_parts[0]
    key = path_parts[1] if len(path_parts) > 1 else ''
    
    return {"bucket": bucket, "key": key}
