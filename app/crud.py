from sqlalchemy.orm import Session
from .models import Usuario
from .schemas import UsuarioCreate
from datetime import datetime, timedelta
import hashlib
import secrets

def gerar_credencial(email: str, dias: int = 30) -> str:
    """Gera uma credencial única para o usuário"""
    validade = (datetime.utcnow() + timedelta(days=dias)).isoformat()
    raw = f"{email}-{validade}-{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()

def criar_usuario(db: Session, usuario: UsuarioCreate):
    """Cria um novo usuário no banco"""
    credencial = gerar_credencial(usuario.email, dias=30)
    db_usuario = Usuario(
        login=usuario.login,
        senha=usuario.senha,
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
    return db.query(Usuario).filter(Usuario.email == email).first()

def atualizar_usuario(db: Session, usuario_id: int, dados: dict):
    """Atualiza dados de um usuário"""
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario:
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