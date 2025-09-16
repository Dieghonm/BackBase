from sqlalchemy.orm import Session
from ..models.user import Usuario
from ..schemas.schemas import UsuarioCreate
from ..utils.security import hash_password
from datetime import datetime
from ..utils.jwt_auth import gerar_credencial

def criar_usuario(db: Session, usuario: UsuarioCreate):
    """Cria um novo usuário no banco com senha criptografada"""
    credencial = gerar_credencial(usuario.email, dias=30)
    db_usuario = Usuario(
        login=usuario.login,
        senha=usuario.senha,  # Já vem hashada do main.py
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
