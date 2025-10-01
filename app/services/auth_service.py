from sqlalchemy.orm import Session
from ..models.user import Usuario
from ..utils.jwt_auth import verify_password
from .user_service import buscar_usuario_por_email, buscar_usuario_por_login


def autenticar_usuario(db: Session, email_ou_login: str, senha: str) -> Usuario | None:
    """
    Autentica um usuário verificando email/login e senha
    
    Args:
        db: Sessão do banco de dados
        email_ou_login: Email ou login do usuário
        senha: Senha em texto plano
        
    Returns:
        Objeto Usuario se autenticação for bem-sucedida, None caso contrário
    """
    usuario = buscar_usuario_por_email(db, email_ou_login)

    if not usuario:
        usuario = buscar_usuario_por_login(db, email_ou_login)
    
    if not usuario:
        return None
    
    if not verify_password(senha, usuario.senha):
        return None
    
    return usuario