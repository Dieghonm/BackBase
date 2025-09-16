from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from ..core.config import settings

# Configuração do banco de dados
DATABASE_URL = settings.database_url

# Engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necessário para SQLite
)

# Classe base para os modelos
Base = declarative_base()