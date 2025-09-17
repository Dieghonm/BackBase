import os
from pydantic_settings import BaseSettings
from typing import Optional, List
from .constants import (
    JWT_EXPIRE_MINUTES, 
    DEFAULT_RATE_LIMITS,
    VALID_USER_TAGS,
    VALID_USER_PLANS
)

class Settings(BaseSettings):
    database_url: str = "sqlite:///./banco.db"
    
    secret_key: str = "dev-super-secret-key-change-in-production-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    jwt_secret_key: str = "dev-super-secret-key-change-in-production-2024"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = JWT_EXPIRE_MINUTES
    
    debug: bool = False
    api_version: str = "1.0.0"
    api_title: str = "BackBase API"
    
    rate_limit_login: str = DEFAULT_RATE_LIMITS['LOGIN']
    rate_limit_cadastro: str = DEFAULT_RATE_LIMITS['CADASTRO']
    
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    @property
    def cors_origins_safe(self) -> List[str]:
        """
        Retorna origins seguros baseado no ambiente
        """
        if self.environment == "development":
            return [
                "http://localhost:3000",
                "http://localhost:8080", 
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080"
            ]
        else:
            production_origins = os.getenv("CORS_ORIGINS", "").split(",")
            return [origin.strip() for origin in production_origins if origin.strip()]

    log_level: str = "INFO"
    log_file: str = "app.log"
    
    environment: Optional[str] = "development"
    port: Optional[int] = 8000
    host: Optional[str] = "0.0.0.0"
    
    @property
    def valid_user_tags(self) -> List[str]:
        """Retorna tags válidas de usuário"""
        return VALID_USER_TAGS
    
    @property  
    def valid_user_plans(self) -> List[str]:
        """Retorna planos válidos de usuário"""
        return VALID_USER_PLANS

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

settings = Settings()