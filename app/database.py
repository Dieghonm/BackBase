from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from .config import settings  # Importar settings
from .utils.jwt_auth import hash_password, gerar_credencial

# Usar a variável do .env
DATABASE_URL = settings.database_url

usuarios_iniciais = [
    {"login": "dieghonm", "email": "dieghonm@gmail.com", "tag": "admin", "senha": "Admin123@"},
    {"login": "cavamaga", "email": "cava.maga@gmail.com", "tag": "admin", "senha": "Admin123@"},
    {"login": "tiaguetevital", "email": "tiagovital999@gmail.com", "tag": "admin", "senha": "Admin123@"},
    {"login": "Pietro", "email": "tester@gmail.com", "tag": "tester", "senha": "Tester123@"},
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
    print(f"🔧 Configurações carregadas do .env:")
    print(f"   - Database: {settings.database_url}")
    print(f"   - Debug Mode: {settings.debug}")
    print(f"   - API Version: {settings.api_version}")

    # Import dentro da função para evitar circular import
    from .models import Usuario

    db = SessionLocal()

    for u in usuarios_iniciais:
        if not db.query(Usuario).filter_by(email=u["email"]).first():
            senha_hashada = hash_password(u["senha"])
            credencial = gerar_credencial(u["email"], dias=365)
            
            
            usuario = Usuario(
                login=u["login"],
                email=u["email"],
                tag=u["tag"],
                senha=senha_hashada,
                plan="admin",
                plan_date=datetime.utcnow(),
                credencial=credencial,
                created_at=datetime.utcnow()
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