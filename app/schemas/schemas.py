from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

class UsuarioCreate(BaseModel):
    login: str
    senha: str
    email: EmailStr
    tag: str = "cliente"
    plan: Optional[str] = None
    
    @validator('login')
    def validate_login(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Login deve ter entre 3 e 50 caracteres')
        if not v.replace('_', '').isalnum():
            raise ValueError('Login deve conter apenas letras, números e underscore')
        return v.lower().strip()
    
    @validator('senha')
    def validate_senha(cls, v):
        if len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        return v.lower().strip()
    
    @validator('tag')
    def validate_tag(cls, v):
        valid_tags = ['admin', 'tester', 'cliente', 'usuario']
        if v not in valid_tags:
            raise ValueError(f'Tag deve ser uma de: {", ".join(valid_tags)}')
        return v
    
    @validator('plan')
    def validate_plan(cls, v):
        if v is None:
            return v
        valid_plans = ['trial', 'mensal', 'trimestral', 'semestral', 'admin']
        if v not in valid_plans:
            raise ValueError(f'Plan deve ser um de: {", ".join(valid_plans)}')
        return v

class LoginRequest(BaseModel):
    email_ou_login: str
    senha: str
    
    @validator('email_ou_login')
    def validate_email_ou_login(cls, v):
        v = v.strip().lower()
        if len(v) < 3:
            raise ValueError('Email ou login deve ter pelo menos 3 caracteres')
        return v
    
    @validator('senha')
    def validate_senha(cls, v):
        if len(v) < 1:
            raise ValueError('Senha é obrigatória')
        return v

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

# 🔥 SCHEMAS ATUALIZADOS PARA TOKEN DE 1 MÊS
class TokenResponse(BaseModel):
    """Resposta do endpoint de login com JWT (válido por 1 mês)"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 2628000  # 🔥 1 MÊS em segundos (30 dias * 24h * 60min * 60seg)
    token_duration: str = "1_month"
    user: dict

class TokenData(BaseModel):
    """Dados extraídos do token JWT"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    login: Optional[str] = None
    tag: Optional[str] = None
    token_duration: Optional[str] = None
