import os
from pydantic_settings import BaseSettings
from typing import Optional, List
from dotenv import load_dotenv
from .constants import (
    JWT_EXPIRE_MINUTES, 
    DEFAULT_RATE_LIMITS,
    VALID_USER_TAGS,
    VALID_USER_PLANS
)

try:
    load_dotenv()
except FileNotFoundError:
    raise FileNotFoundError("❌ Arquivo .env não encontrado! Crie um arquivo .env baseado no .env.example")

missing_vars = []
required_env_vars = [
    "DATABASE_URL",
    "SECRET_KEY", 
    "JWT_SECRET_KEY"
]

for var in required_env_vars:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    raise ValueError(f"❌ Variáveis obrigatórias não encontradas no .env: {', '.join(missing_vars)}")

class Settings(BaseSettings):
    database_url: str = os.environ["DATABASE_URL"]
    
    secret_key: str = os.environ["SECRET_KEY"]
    algorithm: str = os.environ.get("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    jwt_secret_key: str = os.environ["JWT_SECRET_KEY"]
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.environ.get("JWT_EXPIRE_MINUTES", str(JWT_EXPIRE_MINUTES)))
    
    debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
    api_version: str = os.environ.get("API_VERSION", "1.0.0")
    api_title: str = os.environ.get("API_TITLE", "BackBase API")
    
    rate_limit_login: str = os.environ.get("RATE_LIMIT_LOGIN", DEFAULT_RATE_LIMITS['LOGIN'])
    rate_limit_cadastro: str = os.environ.get("RATE_LIMIT_CADASTRO", DEFAULT_RATE_LIMITS['CADASTRO'])
    
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    @property
    def cors_origins_safe(self) -> List[str]:
        if self.environment == "development":
            return [
                "http://localhost:3000",
                "http://localhost:8080", 
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080"
            ]
        else:
            cors_env = os.environ.get("CORS_ORIGINS", "")
            if cors_env:
                try:
                    import json
                    return json.loads(cors_env)
                except:
                    return [origin.strip() for origin in cors_env.split(",")]
            return []

    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_file: str = os.environ.get("LOG_FILE", "app.log")
    
    environment: Optional[str] = os.environ.get("ENVIRONMENT", "development")
    port: Optional[int] = int(os.environ.get("PORT", "8000"))
    host: Optional[str] = os.environ.get("HOST", "0.0.0.0")
    
    @property
    def valid_user_tags(self) -> List[str]:
        return VALID_USER_TAGS
    
    @property  
    def valid_user_plans(self) -> List[str]:
        return VALID_USER_PLANS

    class Config:
        case_sensitive = False
        extra = "allow"

settings = Settings()