import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Banco de dados
    database_url: str = "sqlite:///./banco.db"
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API
    debug: bool = False
    api_version: str = "1.0.0"
    api_title: str = "BackBase API"
    
    # Rate Limiting
    rate_limit_login: str = "5/minute"
    rate_limit_cadastro: str = "3/minute"
    
    # JWT
    jwt_secret_key: str = "sua-chave-secreta-muito-forte-aqui-mude-em-producao"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Cors
    cors_origins: list = ["*"]

    # Logs
    log_level: str = "INFO"
    log_file: str = "app.log"

    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global das configurações
settings = Settings()

