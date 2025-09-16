from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.user import Usuario
from ..schemas.schemas import UsuarioCreate
from ..utils.jwt_auth import hash_password, gerar_credencial  # Usar apenas jwt_auth
from datetime import datetime
from fastapi import HTTPException

def criar_usuario(db: Session, usuario: UsuarioCreate):
    """
    Cria um novo usuário no banco com validações completas
    """
    try:
        # Verifica se já existe usuário com mesmo email
        usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email.lower()).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail="Email já está em uso")
        
        # Verifica se já existe usuário com mesmo login
        login_existente = db.query(Usuario).filter(Usuario.login == usuario.login.lower()).first()
        if login_existente:
            raise HTTPException(status_code=400, detail="Login já está em uso")
        
        # Gera credencial válida por 1 ano
        credencial = gerar_credencial(usuario.email, dias=365)
        
        # Hash da senha se não estiver hasheada
        senha_final = usuario.senha
        if not senha_final.startswith('$2b$'):  # Verifica se já é hash bcrypt
            senha_final = hash_password(senha_final)
        
        db_usuario = Usuario(
            login=usuario.login.lower().strip(),
            senha=senha_final,
            email=usuario.email.lower().strip(),
            tag=usuario.tag,
            plan=usuario.plan,
            plan_date=datetime.utcnow() if usuario.plan else None,
            credencial=credencial,
            created_at=datetime.utcnow()
        )
        
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        
        print(f"✅ Usuário criado: {db_usuario.login} ({db_usuario.email})")
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
        
        # Valida email único se estiver sendo alterado
        if 'email' in dados and dados['email'] != db_usuario.email:
            email_existente = db.query(Usuario).filter(
                Usuario.email == dados['email'].lower(),
                Usuario.id != usuario_id
            ).first()
            if email_existente:
                raise HTTPException(status_code=400, detail="Email já está em uso por outro usuário")
            dados['email'] = dados['email'].lower().strip()
        
        # Valida login único se estiver sendo alterado
        if 'login' in dados and dados['login'] != db_usuario.login:
            login_existente = db.query(Usuario).filter(
                Usuario.login == dados['login'].lower(),
                Usuario.id != usuario_id
            ).first()
            if login_existente:
                raise HTTPException(status_code=400, detail="Login já está em uso por outro usuário")
            dados['login'] = dados['login'].lower().strip()
        
        # Se a senha está sendo atualizada, criptografa ela
        if 'senha' in dados:
            if not dados['senha'].startswith('$2b$'):  # Verifica se já é hash bcrypt
                dados['senha'] = hash_password(dados['senha'])
        
        # Atualiza campos
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

def alterar_senha(db: Session, usuario_id: int, senha_atual: str, senha_nova: str) -> bool:
    """
    Altera a senha de um usuário após verificar a senha atual
    """
    try:
        from ..utils.jwt_auth import verify_password, hash_password
        
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
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao alterar senha: {str(e)}")

