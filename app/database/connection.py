from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from ..core.config import settings

DATABASE_URL = settings.database_url

if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine_config = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "echo": settings.debug
    }
    
    engine = create_engine(DATABASE_URL, **engine_config)

Base = declarative_base()


print(f"✅ Banco configurado: {DATABASE_URL[:30]}...")