import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    database_url: str = "sqlite:///./banco.db"
    
    secret_key: str = "dev-super-secret-key-change-in-production-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    jwt_secret_key: str = "dev-super-secret-key-change-in-production-2024"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    debug: bool = False
    api_version: str = "1.0.0"
    api_title: str = "BackBase API"
    
    rate_limit_login: str = "5/minute"
    rate_limit_cadastro: str = "3/minute"
    
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

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

settings = Settings()