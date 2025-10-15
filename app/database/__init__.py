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
                db.refresh(usuario)
                
                print(f"✅ Usuário inicial criado: {u['login']} ({u['email']})")
                
                enviar_email_boas_vindas_inicial(usuario, "admin")
                
    except Exception as e:
        print(f"❌ Erro ao criar usuários iniciais: {str(e)}")
        db.rollback()
    finally:
        db.close()

def enviar_email_boas_vindas_inicial(usuario, plan: str):
    """
    Envia email de boas-vindas para usuários iniciais
    
    Args:
        usuario: Objeto Usuario criado
        plan: Plano do usuário
    """
    try:
        from ..services.email_service import get_email_service
        
        email_service = get_email_service()
        if not email_service:
            print(f"⚠️  Email service não configurado. Saltando email para {usuario.email}")
            return False
        
        sucesso = email_service.enviar_boas_vindas(
            email=usuario.email,
            login=usuario.login,
            plan=plan
        )
        
        if sucesso:
            print(f"✅ Email de boas-vindas enviado para {usuario.email}")
        else:
            print(f"❌ Falha ao enviar email para {usuario.email}")
        
        return sucesso
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {str(e)}")
        return False

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