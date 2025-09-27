"""
Application configuration using Pydantic Settings
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings using Pydantic Settings"""
    
    # Application
    app_name: str = Field("ms-analytics", description="Application name")
    debug: bool = Field(False, description="Debug mode")
    host: str = Field("0.0.0.0", description="Host to bind")
    port: int = Field(8010, description="Port to bind")
    log_level: str = Field("INFO", description="Logging level")
    
    # Environment
    environment: str = Field("local", description="Environment: local or aws")
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key")
    aws_region: str = Field("us-east-1", description="AWS Region")
    aws_profile: Optional[str] = Field(None, description="AWS Profile for local development")
    
    # AWS S3
    aws_s3_bucket: str = Field("bus-mvp-data-lake", description="S3 bucket for data lake")
    aws_s3_results_bucket: str = Field("bus-mvp-query-results", description="S3 bucket for query results")
    
    # AWS Glue
    aws_glue_catalog_database: str = Field("bus_mvp_catalog", description="Glue catalog database")
    aws_glue_table_prefix: str = Field("bus_mvp_", description="Glue table prefix")
    
    # AWS Athena
    aws_athena_workgroup: str = Field("bus-mvp-analytics", description="Athena workgroup")
    aws_athena_query_timeout: int = Field(300, description="Athena query timeout in seconds")
    aws_athena_max_results: int = Field(10000, description="Maximum query results")
    query_output_path: str = Field(
        "s3://bus-mvp-query-results/athena-outputs/",
        description="S3 path for query outputs"
    )
    
    # Cache settings (optional)
    cache_ttl: int = Field(300, description="Cache TTL in seconds")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(100, description="Rate limit per minute")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @property
    def is_local_environment(self) -> bool:
        """Check if running in local environment"""
        return self.environment.lower() == "local"
    
    @property
    def is_aws_environment(self) -> bool:
        """Check if running in AWS environment"""
        return self.environment.lower() == "aws"


# Global settings instance
settings = Settings()
