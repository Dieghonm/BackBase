from sqlalchemy.orm import sessionmaker
from .connection import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    DepEdency para obter sessão do banco de dados
    Usado como depEdency injection no FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  