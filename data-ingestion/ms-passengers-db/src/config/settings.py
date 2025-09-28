"""
Configuration settings for MS-Passengers Database Ingestion
Using Pydantic Settings for environment-based configuration
"""

from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path


class DatabaseSettings(BaseSettings):
    """PostgreSQL database connection settings"""
    
    host: str = Field(default="sql-db1", env="SQL1_HOST")
    port: int = Field(default=5432, env="SQL1_PORT")
    database: str = Field(default="passengers_db", env="SQL1_DB")
    user: str = Field(default="passengers_user", env="SQL1_USER")
    password: str = Field(default="change_me_sql1_password", env="SQL1_PASSWORD")
    
    # Connection pool settings
    pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # SSL settings
    ssl_mode: str = Field(default="prefer", env="DB_SSL_MODE")
    ssl_cert: Optional[str] = Field(default=None, env="DB_SSL_CERT")
    ssl_key: Optional[str] = Field(default=None, env="DB_SSL_KEY")
    ssl_ca: Optional[str] = Field(default=None, env="DB_SSL_CA")
    
    @property
    def connection_url(self) -> str:
        """Build PostgreSQL connection URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_connection_url(self) -> str:
        """Build async PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class ObjectStorageSettings(BaseSettings):
    """AWS S3 object storage configuration"""
    
    bucket: str = Field(default="bus-mvp-data-lake", env="AWS_S3_BUCKET")
    region: str = Field(default="us-east-1", env="AWS_REGION")
    
    # AWS S3 settings
    aws_access_key_id: str = Field(env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(env="AWS_SECRET_ACCESS_KEY")
    
    # Storage paths
    base_path: str = Field(default="ms-passengers", env="STORAGE_BASE_PATH")


class IngestionSettings(BaseSettings):
    """Data ingestion configuration"""
    
    # Extraction settings
    extraction_interval: int = Field(default=300, env="EXTRACTION_INTERVAL")  # 5 minutes
    batch_size: int = Field(default=1000, env="BATCH_SIZE")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: int = Field(default=60, env="RETRY_DELAY")
    
    # CDC settings
    cdc_enabled: bool = Field(default=True, env="CDC_ENABLED")
    cdc_slot_name: str = Field(default="passengers_ingestion_slot", env="CDC_SLOT_NAME")
    cdc_publication_name: str = Field(default="passengers_publication", env="CDC_PUBLICATION_NAME")
    
    # Full sync settings
    full_sync_enabled: bool = Field(default=True, env="FULL_SYNC_ENABLED")
    full_sync_hour: int = Field(default=2, env="FULL_SYNC_HOUR")  # 2 AM
    full_sync_interval: int = Field(default=86400, env="FULL_SYNC_INTERVAL")  # 24 hours
    
    # Data quality
    quality_threshold: float = Field(default=0.95, env="DATA_QUALITY_THRESHOLD")
    enable_validation: bool = Field(default=True, env="ENABLE_DATA_VALIDATION")
    
    # Parallel processing
    parallel_workers: int = Field(default=2, env="PARALLEL_WORKERS")
    worker_timeout: int = Field(default=300, env="WORKER_TIMEOUT")


class RedisSettings(BaseSettings):
    """Redis cache configuration"""
    
    enabled: bool = Field(default=True, env="REDIS_ENABLED")
    url: str = Field(default="redis://redis-cache:6379", env="REDIS_URL")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Cache settings
    default_ttl: int = Field(default=3600, env="REDIS_DEFAULT_TTL")
    max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")


class MonitoringSettings(BaseSettings):
    """Monitoring and metrics configuration"""
    
    # Prometheus metrics
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=8091, env="METRICS_PORT")
    
    # Health check
    health_check_port: int = Field(default=8090, env="HEALTH_CHECK_PORT")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    @validator("log_level")
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()


class Settings(BaseSettings):
    """Main application settings"""
    
    # Application info
    app_name: str = Field(default="ms-passengers-db-ingestion", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    storage: ObjectStorageSettings = ObjectStorageSettings()
    ingestion: IngestionSettings = IngestionSettings()
    redis: RedisSettings = RedisSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    # Docker and networking
    container_name: str = Field(default="bus-mvp-passengers-ingestion", env="CONTAINER_NAME")
    docker_network: str = Field(default="bus-mvp-network", env="DOCKER_NETWORK")
    
    # Directories
    data_dir: Path = Field(default=Path("/app/data"), env="DATA_DIR")
    logs_dir: Path = Field(default=Path("/app/logs"), env="LOGS_DIR")
    temp_dir: Path = Field(default=Path("/app/temp"), env="TEMP_DIR")
    config_dir: Path = Field(default=Path("/app/config"), env="CONFIG_DIR")
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v
    
    @property
    def health_check_port(self) -> int:
        """Alias for monitoring health check port"""
        return self.monitoring.health_check_port
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.data_dir, self.logs_dir, self.temp_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
