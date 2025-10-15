import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from .constants import (
    JWT_EXPIRE_MINUTES, 
    DEFAULT_RATE_LIMITS,
    VALID_USER_TAGS,
    VALID_USER_PLANS
)

# --- Detectar e carregar ambiente ---
def detect_environment() -> str:
    production_keys = [
        "RENDER", "RAILWAY_ENVIRONMENT", "VERCEL",
        "HEROKU_APP_NAME", "FLY_APP_NAME", "DOKKU_APP_NAME"
    ]
    if any(os.getenv(key) for key in production_keys):
        return "production"
    return os.getenv("ENVIRONMENT", "development").lower()


def setup_environment():
    env = detect_environment()
    if env == "development":
        if load_dotenv():
            print("🔧 Ambiente: DESENVOLVIMENTO — .env carregado com sucesso!")
        else:
            print("⚠️  Ambiente: DESENVOLVIMENTO — arquivo .env não encontrado!")
    else:
        print(f"🚀 Ambiente: PRODUÇÃO ({env.upper()})")
    return env

environment = setup_environment()

# --- Função para verificar variáveis obrigatórias ---
def verify_env_vars(required_vars: List[str]):
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
            print(f"⚠️  Variável obrigatória '{var}' não encontrada no .env!")
    if missing_vars:
        raise ValueError(f"❌ Variáveis obrigatórias ausentes: {', '.join(missing_vars)}")
    print("✅ Todas as variáveis obrigatórias estão presentes no .env!")

required_env_vars = [
    "DATABASE_URL",
    "SECRET_KEY",
    "JWT_SECRET_KEY",
    "BREVO_API_KEY",
    "BREVO_SENDER_EMAIL",
    "BREVO_SENDER_NAME",
    "EMAIL_ENABLED"
]

verify_env_vars(required_env_vars)

# --- Classe Settings ---
class Settings(BaseSettings):
    environment: str = environment
    database_url: str = os.environ["DATABASE_URL"]
    secret_key: str = os.environ["SECRET_KEY"]
    algorithm: str = os.environ.get("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    jwt_secret_key: str = os.environ["JWT_SECRET_KEY"]
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.environ.get("JWT_EXPIRE_MINUTES", str(JWT_EXPIRE_MINUTES)))

    debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
    api_version: str = os.environ.get("API_VERSION", "1.0.0")
    api_title: str = os.environ.get("API_TITLE", "Enden Map")

    rate_limit_login: str = os.environ.get("RATE_LIMIT_LOGIN", DEFAULT_RATE_LIMITS['LOGIN'])
    rate_limit_cadastro: str = os.environ.get("RATE_LIMIT_CADASTRO", DEFAULT_RATE_LIMITS['CADASTRO'])
    rate_limit_tempkey: str = os.environ.get("RATE_LIMIT_TEMKEY", DEFAULT_RATE_LIMITS['TEMPKEY'])

    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_file: str = os.environ.get("LOG_FILE", "app.log")

    port: int = int(os.environ.get("PORT", "8000"))
    host: str = os.environ.get("HOST", "0.0.0.0")

    brevo_api_key: str = os.environ["BREVO_API_KEY"]
    brevo_sender_email: str = os.environ["BREVO_SENDER_EMAIL"]
    brevo_sender_name: str = os.environ["BREVO_SENDER_NAME"]
    email_enabled: bool = os.environ["EMAIL_ENABLED"].lower() == "true"

    @property
    def cors_origins_safe(self) -> List[str]:
        if self.environment == "development":
            return [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://localhost:8080",
                "http://localhost:8081",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080",
                "http://127.0.0.1:8081",
                "exp://192.168.1.1:19000",
                "http://192.168.1.1:8081",
            ]
        else:
            cors_env = os.environ.get("CORS_ORIGINS", "")
            if cors_env:
                try:
                    import json
                    return json.loads(cors_env)
                except:
                    return [origin.strip() for origin in cors_env.split(",")]
            return [
                "https://seu-frontend.vercel.app",
                "https://seu-app.netlify.app",
                "https://localhost:3000"
            ]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def database_config(self) -> dict:
        if "sqlite" in self.database_url:
            return {"check_same_thread": False}
        else:
            return {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30,
                "pool_recycle": 1800
            }

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

