from datetime import datetime
from .session import SessionLocal
from ..utils.jwt_auth import hash_password, gerar_credencial

# Dados dos usuários iniciais
usuarios_iniciais = [
    {"login": "dieghonm", "email": "dieghonm@gmail.com", "tag": "admin", "senha": "Admin123@"},
    {"login": "cavamaga", "email": "cava.maga@gmail.com", "tag": "admin", "senha": "Admin123@"},
    {"login": "tiaguetevital", "email": "tiagovital999@gmail.com", "tag": "admin", "senha": "Admin123@"},
    {"login": "Pietro", "email": "tester@gmail.com", "tag": "tester", "senha": "Tester123@"},
]

def criar_usuarios_iniciais():
    """
    Cria usuários iniciais se eles não existirem
    """
    # Import dentro da função para evitar circular import
    from ..models.user import Usuario
    
    db = SessionLocal()
    
    try:
        for u in usuarios_iniciais:
            # Verifica se usuário já existe
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
                print(f"Usuário inicial criado: {u['login']} ({u['email']})")
            else:
                print(f"Usuário já existe: {u['login']} ({u['email']})")
        
        db.commit()
        print("✅ Usuários iniciais criados/verificados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários iniciais: {str(e)}")
        db.rollback()
    finally:
        db.close()