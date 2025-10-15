from .connection import Base, engine, DATABASE_URL
from .session import SessionLocal, get_db

def criar_tabelas():
    """
    Função que cria as tabelas no banco
    """
    Base.metadata.create_all(bind=engine)

def criar_usuarios_iniciais():
    """
    Cria usuários iniciais se eles não existirem
    """
    from ..models.user import Usuario
    from ..utils.jwt_auth import hash_password
    from datetime import datetime
    
    usuarios_iniciais = [
        {"login": "dieghonm", "email": "dieghonm@gmail.com", "tag": "admin", "senha": "Admin123@"},
        {"login": "cavamaga", "email": "cava.maga@gmail.com", "tag": "admin", "senha": "Admin123@"},
        {"login": "tiaguetevital", "email": "tiagovital999@gmail.com", "tag": "admin", "senha": "Admin123@"},
        {"login": "Pietro", "email": "tester@gmail.com", "tag": "tester", "senha": "Tester123@"},
    ]
    
    db = SessionLocal()
    
    try:
        for u in usuarios_iniciais:
            if not db.query(Usuario).filter_by(email=u["email"]).first():
                senha_hashada = hash_password(u["senha"])
                
                usuario = Usuario(
                    login=u["login"],
                    email=u["email"],
                    tag=u["tag"],
                    senha=senha_hashada,
                    plan="admin",
                    plan_date=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                db.add(usuario)
        db.commit()
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários iniciais: {str(e)}")
        db.rollback()
    finally:
        db.close()

def inicializar_banco():
    """
    Função que inicializa o banco completamente:
    1. Cria tabelas
    2. Cria usuários iniciais
    """
    criar_tabelas()
    criar_usuarios_iniciais()

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
