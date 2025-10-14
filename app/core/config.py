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

# Detectar ambiente automaticamente
def detect_environment():
    """Detecta o ambiente baseado em variáveis disponíveis"""
    if os.environ.get("RENDER"):  # Render define esta variável
        return "production"
    elif os.environ.get("RAILWAY_ENVIRONMENT"):  # Railway
        return "production" 
    elif os.environ.get("VERCEL"):  # Vercel
        return "production"
    elif os.environ.get("HEROKU_APP_NAME"):  # Heroku
        return "production"
    else:
        return "development"

# Carregar .env apenas em desenvolvimento
environment = detect_environment()
if environment == "development":
    try:
        load_dotenv()
        print("🔧 Ambiente: DESENVOLVIMENTO (carregando .env)")
    except FileNotFoundError:
        print("⚠️  Arquivo .env não encontrado em desenvolvimento!")
else:
    print(f"🚀 Ambiente: PRODUÇÃO ({environment.upper()})")

# Verificar variáveis obrigatórias
required_env_vars = [
    "DATABASE_URL",
    "SECRET_KEY", 
    "JWT_SECRET_KEY"
]

missing_vars = []
for var in required_env_vars:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    raise ValueError(f"❌ Variáveis obrigatórias não encontradas: {', '.join(missing_vars)}")

class Settings(BaseSettings):
    # Detectar ambiente
    environment: str = environment
    
    # Banco de dados
    database_url: str = os.environ["DATABASE_URL"]
    
    # Segurança
    secret_key: str = os.environ["SECRET_KEY"]
    algorithm: str = os.environ.get("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # JWT
    jwt_secret_key: str = os.environ["JWT_SECRET_KEY"]
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.environ.get("JWT_EXPIRE_MINUTES", str(JWT_EXPIRE_MINUTES)))
    
    # App configs
    debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
    api_version: str = os.environ.get("API_VERSION", "1.0.0")
    api_title: str = os.environ.get("API_TITLE", "BackBase API")
    
    # Rate limiting
    rate_limit_login: str = os.environ.get("RATE_LIMIT_LOGIN", DEFAULT_RATE_LIMITS['LOGIN'])
    rate_limit_cadastro: str = os.environ.get("RATE_LIMIT_CADASTRO", DEFAULT_RATE_LIMITS['CADASTRO'])
    rate_limit_tempkey: str = os.environ.get("RATE_LIMIT_TEMKEY", DEFAULT_RATE_LIMITS['TEMPKEY'])
    
    # Logs
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_file: str = os.environ.get("LOG_FILE", "app.log")
    
    # Servidor
    port: Optional[int] = int(os.environ.get("PORT", "8000"))
    host: Optional[str] = os.environ.get("HOST", "0.0.0.0")
    
    @property
    def cors_origins_safe(self) -> List[str]:
        """Configuração de CORS baseada no ambiente"""
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
            
            # Fallback para produção
            return [
                "https://seu-frontend.vercel.app",  # Substitua pelo seu domínio
                "https://seu-app.netlify.app",     # Substitua pelo seu domínio
                "https://localhost:3000"           # Para testes locais
            ]

    @property
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.environment == "production"
    
    @property
    def database_config(self) -> dict:
        """Configurações específicas do banco baseadas no ambiente"""
        if "sqlite" in self.database_url:
            return {"check_same_thread": False}
        else:
            # PostgreSQL/MySQL configs para produção
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

# Log das configurações carregadas
print(f"✅ Configurações carregadas:")
print(f"   - Ambiente: {settings.environment}")
print(f"   - Debug: {settings.debug}")
print(f"   - Database: {settings.database_url[:20]}...")
print(f"   - Host: {settings.host}:{settings.port}")
print(f"   - CORS Origins: {len(settings.cors_origins_safe)} origens configuradas")