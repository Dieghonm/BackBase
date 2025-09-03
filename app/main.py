from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import hashlib
import secrets

app = FastAPI()
DATABASE_URL = "sqlite:///./banco.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    tag = Column(String, nullable=False, default="cliente")
    plan = Column(String, nullable=True)
    plan_date = Column(DateTime, nullable=True)
    credencial = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class UsuarioCreate(BaseModel):
    login: str
    senha: str
    email: EmailStr
    tag: str = "cliente"
    plan: str | None = None

def gerar_credencial(email: str, dias: int = 30) -> str:
    validade = (datetime.utcnow() + timedelta(days=dias)).isoformat()
    raw = f"{email}-{validade}-{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()

@app.post("/cadastro")
def cadastrar_usuario(usuario: UsuarioCreate):
    db = SessionLocal()
    try:
        credencial = gerar_credencial(usuario.email, dias=30)
        novo_usuario = Usuario(
            login=usuario.login,
            senha=usuario.senha,
            email=usuario.email,
            tag=usuario.tag,
            plan=usuario.plan,
            plan_date=datetime.utcnow(),
            credencial=credencial,
            created_at=datetime.utcnow()
        )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return {
            "sucesso": True,
            "id": novo_usuario.id,
            "credencial": novo_usuario.credencial,
            "created_at": novo_usuario.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao cadastrar: {str(e)}")
    finally:
        db.close()

@app.get("/usuarios")
def listar_usuarios():
    db = SessionLocal()
    usuarios = db.query(Usuario).all()
    db.close()
    return [
        {
            "id": u.id,
            "login": u.login,
            "email": u.email,
            "tag": u.tag,
            "plan": u.plan,
            "plan_date": u.plan_date,
            "credencial": u.credencial,
            "created_at": u.created_at
        }
        for u in usuarios
    ]

def main():
    print("FastAPI app configurado com sucesso!")