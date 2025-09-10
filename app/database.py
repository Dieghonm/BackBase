from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = "sqlite:///./banco.db"

usuarios_iniciais = [
    {"login": "dieghonm", "email": "dieghonm@gmail.com", "tag": "admin"},
    {"login": "cavamaga", "email": "cava.maga@gmail.com", "tag": "admin"},
    {"login": "tiaguetevital", "email": "tiagovital999@gmail.com", "tag": "admin"},
    {"login": "Pietro", "email": "tester@gmail.com", "tag": "tester"},
    ]

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def criar_tabelas():
    """Verifica se o banco existe, cria as tabelas e usuários iniciais"""
    if not os.path.exists("banco.db"):
        print("Banco de dados não encontrado. Criando novo banco...")
    else:
        print("Banco de dados encontrado.")
    
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas/verificadas com sucesso!")

    # Import dentro da função para evitar circular import
    from .models import Usuario

    db = SessionLocal()

    for u in usuarios_iniciais:
        if not db.query(Usuario).filter_by(email=u["email"]).first():
            usuario = Usuario(
                login=u["login"],
                email=u["email"],
                tag=u["tag"],
                senha="Teste123@",   # valor padrão só para criação inicial
                plan="admin",        # valor padrão só para criação inicial
                plan_date=datetime.utcnow()
            )
            db.add(usuario)

    db.commit()
    db.close()

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
