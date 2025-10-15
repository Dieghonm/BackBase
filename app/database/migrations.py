import os
from .connection import Base, engine
from ..core.config import settings

def criar_tabelas():
    """
    Verifica se o banco existe e cria as tabelas necessárias
    """
    if "sqlite" in settings.database_url:
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