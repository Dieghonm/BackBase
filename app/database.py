from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "sqlite:///./banco.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def criar_tabelas():
    """Verifica se o banco existe e cria as tabelas se necessário"""
    if not os.path.exists("banco.db"):
        print("Banco de dados não encontrado. Criando novo banco...")
    else:
        print("Banco de dados encontrado.")
    
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas/verificadas com sucesso!")

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()