from sqlalchemy.orm import sessionmaker
from .connection import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency para obter sessão do banco de dados
    Usado como dependency injection no FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()