from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings
    Lee automáticamente desde variables de entorno
    """
    
    # AWS Configuration
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str = ""
    aws_default_region: str = "us-east-1"
    
    # Athena Configuration
    glue_database: str = "bus_mvp_db"
    athena_output_location: str = "s3://bus-mvp-datalake/athena-results/"
    athena_query_timeout: int = 60  # segundos
    
    # Application
    app_name: str = "Bus MVP Analytics API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Retorna singleton de settings (cached)"""
    return Settings()
