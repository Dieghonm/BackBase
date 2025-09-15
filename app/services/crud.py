from sqlalchemy.orm import Session
from ..models.models import Usuario
from ..schemas.schemas import UsuarioCreate
from ..utils.security import hash_password, verify_password
from datetime import datetime, timedelta
from ..utils.jwt_auth import (
gerar_credencial
)


def criar_usuario(db: Session, usuario: UsuarioCreate):
    """Cria um novo usuário no banco com senha criptografada"""
    # ✅ CORREÇÃO: Não faz hash aqui, pois já vem hashada do main.py
    # senha_hash = hash_password(usuario.senha)  # ❌ REMOVER ESTA LINHA
    
    credencial = gerar_credencial(usuario.email, dias=30)
    db_usuario = Usuario(
        login=usuario.login,
        senha=usuario.senha,  # ✅ Usa a senha que já vem hashada
        email=usuario.email,
        tag=usuario.tag,
        plan=usuario.plan,
        plan_date=datetime.utcnow() if usuario.plan else None,
        credencial=credencial,
        created_at=datetime.utcnow()
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

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
    # Busca usuário por email ou login
    usuario = buscar_usuario_por_email(db, email_ou_login)
    if not usuario:
        usuario = buscar_usuario_por_login(db, email_ou_login)
    
    if not usuario:
        return None
    
    # Verifica se a senha está correta
    if not verify_password(senha, usuario.senha):
        return None
    
    return usuario

def listar_usuarios(db: Session):
    """Lista todos os usuários"""
    return db.query(Usuario).all()

def buscar_usuario_por_id(db: Session, usuario_id: int):
    """Busca usuário por ID"""
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def buscar_usuario_por_email(db: Session, email: str):
    """Busca usuário por email"""
    return db.query(Usuario).filter(Usuario.email == email.lower()).first()

def buscar_usuario_por_login(db: Session, login: str):
    """Busca usuário por login"""
    return db.query(Usuario).filter(Usuario.login == login.lower()).first()

def atualizar_usuario(db: Session, usuario_id: int, dados: dict):
    """Atualiza dados de um usuário"""
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario:
        # Se a senha está sendo atualizada, criptografa ela
        if 'senha' in dados:
            dados['senha'] = hash_password(dados['senha'])
        
        for key, value in dados.items():
            setattr(db_usuario, key, value)
        db.commit()
        db.refresh(db_usuario)
    return db_usuario

def deletar_usuario(db: Session, usuario_id: int):
    """Deleta um usuário"""
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario:
        db.delete(db_usuario)
        db.commit()
    return db_usuario

def alterar_senha(db: Session, usuario_id: int, senha_atual: str, senha_nova: str) -> bool:
    """
    Altera a senha de um usuário após verificar a senha atual
    
    Args:
        db: Sessão do banco de dados
        usuario_id: ID do usuário
        senha_atual: Senha atual em texto plano
        senha_nova: Nova senha em texto plano
        
    Returns:
        True se a senha foi alterada com sucesso, False caso contrário
    """
    from ..utils.security import verify_password, hash_password
    
    usuario = buscar_usuario_por_id(db, usuario_id)
    if not usuario:
        return False
    
    # Verifica se a senha atual está correta
    if not verify_password(senha_atual, usuario.senha):
        return False
    
    # Atualiza com a nova senha criptografada
    usuario.senha = hash_password(senha_nova)
    db.commit()
    return True