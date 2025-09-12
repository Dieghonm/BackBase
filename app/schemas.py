from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuarioCreate(BaseModel):
    login: str
    senha: str
    email: EmailStr
    tag: str = "cliente"
    plan: Optional[str] = None

class LoginRequest(BaseModel):
    email_ou_login: str
    senha: str

class UsuarioResponse(BaseModel):
    id: int
    login: str
    email: str
    tag: str
    plan: Optional[str]
    plan_date: Optional[datetime]
    credencial: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# ✨ NOVOS SCHEMAS PARA JWT
class TokenResponse(BaseModel):
    """Resposta do endpoint de login com JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutos em segundos
    user: dict

class TokenData(BaseModel):
    """Dados extraídos do token JWT"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    login: Optional[str] = None
    tag: Optional[str] = None
    