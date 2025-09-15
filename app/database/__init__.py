# Imports principais para manter compatibilidade
from .connection import Base, engine, DATABASE_URL
from .session import SessionLocal, get_db
from .migrations import criar_tabelas
from .seeds import criar_usuarios_iniciais

# Função combinada para inicialização completa
def inicializar_banco():
    """
    Função que inicializa o banco completamente:
    1. Cria tabelas
    2. Cria usuários iniciais
    """
    print("🚀 Inicializando banco de dados...")
    criar_tabelas()
    criar_usuarios_iniciais()
    print("✅ Banco inicializado com sucesso!")

# Exports para manter compatibilidade com código existente
__all__ = [
    'Base',
    'engine', 
    'DATABASE_URL',
    'SessionLocal',
    'get_db',
    'criar_tabelas',
    'criar_usuarios_iniciais',
    'inicializar_banco'
]