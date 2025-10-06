from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings
    Lee automáticamente desde variables de entorno
    
    NOTA: Las variables se leen desde el .env centralizado en la raíz del proyecto
    cuando se ejecuta con Docker Compose. Para desarrollo local, las variables
    deben estar en el entorno del sistema o en un .env en la raíz del proyecto.
    """
    
    # AWS Configuration
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str = ""
    aws_default_region: str = "us-east-1"
    
    # Athena Configuration
    glue_database: str = "bus_mvp_db"
    athena_output_location: str = "s3://bus-mvp-datalake-1/athena-results/"
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
        # Cuando se ejecuta con Docker Compose, las variables vienen del environment
        # Para desarrollo local, intenta cargar desde .env en varios paths
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Permite que las variables de entorno del sistema sobrescriban el .env
        env_nested_delimiter = "__"

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna singleton de settings (cached)
    
    En Docker Compose, las variables se inyectan como environment variables
    desde el .env centralizado en la raíz del proyecto.
    """
    return Settings()

