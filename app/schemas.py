from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional

class UsuarioCreate(BaseModel):
    login: str
    senha: str
    email: EmailStr
    tag: str = "cliente"
    plan: Optional[str] = None

    @field_validator('senha')
    @classmethod
    def validate_password(cls, v):
        """Valida se a senha atende aos critérios de segurança"""
        # Importação local para evitar problemas de import circular
        from app.utils.security import is_password_strong
        
        is_strong, errors = is_password_strong(v)
        if not is_strong:
            raise ValueError(f"Senha não atende aos critérios de segurança: {'; '.join(errors)}")
        
        return v
    
    @field_validator('login')
    @classmethod
    def validate_login(cls, v):
        """Valida o formato do login"""
        if len(v) < 3:
            raise ValueError("Login deve ter pelo menos 3 caracteres")
        if len(v) > 50:
            raise ValueError("Login deve ter no máximo 50 caracteres")
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError("Login deve conter apenas letras, números, underscore e ponto")
        return v.lower()

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Normaliza o email"""
        return v.lower()

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