from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.user import Usuario
from ..schemas.schemas import UsuarioCreate
from ..utils.jwt_auth import hash_password, verify_password
from datetime import datetime
from fastapi import HTTPException

def criar_usuario(db: Session, usuario: UsuarioCreate):
    """
    Cria um novo usuário no banco com validações completas
    """
    try:
        usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email.lower()).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail="Email já está em uso")
        
        login_existente = db.query(Usuario).filter(Usuario.login == usuario.login.lower()).first()
        if login_existente:
            raise HTTPException(status_code=400, detail="Login já está em uso")
        
        senha_final = usuario.senha
        if not senha_final.startswith('$2b$'):
            senha_final = hash_password(senha_final)
        
        db_usuario = Usuario(
            login=usuario.login.lower().strip(),
            senha=senha_final,
            email=usuario.email.lower().strip(),
            tag=usuario.tag,
            plan=usuario.plan,
            plan_date=datetime.utcnow() if usuario.plan else None,
            created_at=datetime.utcnow()
        )
        
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        
        return db_usuario
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Dados duplicados: email ou login já existe")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")


def listar_usuarios(db: Session):
    """Lista todos os usuários ativos"""
    return db.query(Usuario).all()


def buscar_usuario_por_id(db: Session, usuario_id: int):
    """Busca usuário por ID"""
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def buscar_usuario_por_email(db: Session, email: str):
    """Busca usuário por email"""
    email = email.lower().strip()
    return db.query(Usuario).filter(Usuario.email == email).first()


def buscar_usuario_por_login(db: Session, login: str):
    """Busca usuário por login"""
    login = login.lower().strip()
    return db.query(Usuario).filter(Usuario.login == login).first()


def atualizar_usuario(db: Session, usuario_id: int, dados: dict):
    """
    Atualiza dados de um usuário com validações
    """
    try:
        db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not db_usuario:
            return None
        
        if 'email' in dados and dados['email'] != db_usuario.email:
            email_existente = db.query(Usuario).filter(
                Usuario.email == dados['email'].lower(),
                Usuario.id != usuario_id
            ).first()
            if email_existente:
                raise HTTPException(status_code=400, detail="Email já está em uso por outro usuário")
            dados['email'] = dados['email'].lower().strip()
        
        if 'login' in dados and dados['login'] != db_usuario.login:
            login_existente = db.query(Usuario).filter(
                Usuario.login == dados['login'].lower(),
                Usuario.id != usuario_id
            ).first()
            if login_existente:
                raise HTTPException(status_code=400, detail="Login já está em uso por outro usuário")
            dados['login'] = dados['login'].lower().strip()
        
        if 'senha' in dados:
            if not dados['senha'].startswith('$2b$'):
                dados['senha'] = hash_password(dados['senha'])
        
        for key, value in dados.items():
            if hasattr(db_usuario, key):
                setattr(db_usuario, key, value)
        
        db.commit()
        db.refresh(db_usuario)
        
        return db_usuario
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")


def deletar_usuario(db: Session, usuario_id: int):
    """Deleta um usuário permanentemente"""
    try:
        db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if db_usuario:
            db.delete(db_usuario)
            db.commit()
            return db_usuario
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar usuário: {str(e)}")


def enviar_email_boas_vindas(usuario, plan: str = "trial"):
    """
    Envia email de boas-vindas após cadastro
    
    Args:
        usuario: Objeto Usuario criado
        plan: Plano do usuário
    """
    try:
        from .email_service import get_email_service
        
        email_service = get_email_service()
        if not email_service:
            print(f"⚠️  Email service não configurado. Saltando email para {usuario.email}")
            return False
        
        sucesso = email_service.enviar_boas_vindas(
            email=usuario.email,
            login=usuario.login,
            plan=plan or "trial"
        )
        
        if sucesso:
            print(f"✅ Email de boas-vindas enviado para {usuario.email}")
        else:
            print(f"❌ Falha ao enviar email para {usuario.email}")
        
        return sucesso
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {str(e)}")
        return False


def alterar_senha(db: Session, usuario_id: int, senha_atual: str, senha_nova: str) -> bool:
    """
    Altera a senha de um usuário após verificar a senha atual
    """
    try:
        usuario = buscar_usuario_por_id(db, usuario_id)
        if not usuario:
            return False
        
        if not verify_password(senha_atual, usuario.senha):
            return False
        
        usuario.senha = hash_password(senha_nova)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao alterar senha: {str(e)}")
    

def recuperar_senha(
    db: Session, 
    email_ou_login: str, 
    tempkey: str, 
    nova_senha: str
) -> tuple[bool, str]:
    """
    Altera a senha de um usuário usando o tempkey como validação
    
    Args:
        db: Sessão do banco de dados
        email_ou_login: Email ou login do usuário
        tempkey: Código de 4 dígitos enviado por email
        nova_senha: Nova senha em texto plano
    
    Returns:
        Tupla (sucesso: bool, mensagem: str)
    """
    try:
        # 1. Buscar o usuário
        usuario = buscar_usuario_por_email(db, email_ou_login)
        if not usuario:
            usuario = buscar_usuario_por_login(db, email_ou_login)
        
        if not usuario:
            return False, "Usuário não encontrado"
        
        # 2. Validar se existe temp_senha e temp_senha_expira
        if not usuario.temp_senha or not usuario.temp_senha_expira:
            return False, "Nenhuma solicitação de recuperação de senha ativa"
        
        # 3. Validar se o tempkey ainda está válido
        if datetime.utcnow() > usuario.temp_senha_expira:
            # Limpar o tempkey expirado
            usuario.temp_senha = None
            usuario.temp_senha_expira = None
            db.commit()
            return False, "Código de recuperação expirado. Solicite um novo."
        
        # 4. Validar o tempkey comparando com o hash armazenado
        if not verify_password(tempkey, usuario.temp_senha):
            return False, "Código de recuperação inválido"
        
        # 5. Hash da nova senha
        senha_hashada = hash_password(nova_senha)
        
        # 6. Atualizar a senha e limpar o tempkey
        usuario.senha = senha_hashada
        usuario.temp_senha = None
        usuario.temp_senha_expira = None
        
        db.commit()
        db.refresh(usuario)
        
        return True, "Senha alterada com sucesso"
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao recuperar senha: {str(e)}")
        return False, f"Erro ao alterar senha: {str(e)}"
