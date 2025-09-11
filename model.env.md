# === CONFIGURAÇÕES DE DESENVOLVIMENTO ===
# Banco de dados
DATABASE_URL=sqlite:///./banco.db

# JWT - Chave super secreta (NUNCA commitar!)
SECRET_KEY=sua-chave-super-mega-ultra-secreta-de-256-bits-aqui-123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
DEBUG=true
API_VERSION=1.0.0
API_TITLE=BackBase API

# Rate Limiting
RATE_LIMIT_LOGIN=5/minute
RATE_LIMIT_CADASTRO=3/minute

# Logs
LOG_LEVEL=INFO
LOG_FILE=app.log