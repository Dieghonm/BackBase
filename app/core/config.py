import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Banco de dados
    database_url: str = "sqlite:///./banco.db"
    
    # JWT
    secret_key: str = "dev-super-secret-key-change-in-production-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # JWT específicas (compatibilidade)
    jwt_secret_key: str = "dev-super-secret-key-change-in-production-2024"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # API
    debug: bool = False
    api_version: str = "1.0.0"
    api_title: str = "BackBase API"
    
    # Rate Limiting
    rate_limit_login: str = "5/minute"
    rate_limit_cadastro: str = "3/minute"
    
    # CORS - usando List ao invés de string
    cors_origins: List[str] = ["*"]

    # Logs
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    # Configurações extras permitidas
    environment: Optional[str] = "development"
    port: Optional[int] = 8000
    host: Optional[str] = "0.0.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False
        # Permite campos extras do .env que não estão definidos na classe
        extra = "allow"

# Instância global das configurações
settings = Settings()