from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional
from ..core.constants import VALID_USER_TAGS, VALID_USER_PLANS, MIN_PASSWORD_LENGTH

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
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        return v.lower().strip()
    
    @validator('tag')
    def validate_tag(cls, v):
        if v not in VALID_USER_TAGS:
            raise ValueError(f'Tag deve ser uma de: {", ".join(VALID_USER_TAGS)}')
        return v
    
    @validator('plan')
    def validate_plan(cls, v):
        if v is None:
            return v
        if v not in VALID_USER_PLANS:
            raise ValueError(f'Plan deve ser um de: {", ".join(VALID_USER_PLANS)}')
        return v

class LoginRequest(BaseModel):
    """Schema para login com credenciais OU token"""
    email_ou_login: Optional[str] = None
    tempKey: Optional[int] = None
    senha: Optional[str] = None
    token: Optional[str] = None
    
    @validator('token')
    def validate_inputs(cls, v, values):
        """Valida que PELO MENOS um método foi fornecido"""
        email_ou_login = values.get('email_ou_login')
        senha = values.get('senha')
        
        if v:
            if email_ou_login or senha:
                raise ValueError('Forneça apenas TOKEN ou EMAIL/SENHA, não ambos')
            return v.strip()
        
        if not email_ou_login or not senha:
            raise ValueError('Forneça TOKEN ou EMAIL/SENHA')
        
        return v
    
    @validator('email_ou_login')
    def validate_email_ou_login(cls, v):
        if v:
            v = v.strip().lower()
            if len(v) < 3:
                raise ValueError('Email ou login deve ter pelo menos 3 caracteres')
        return v
    
    @validator('senha')
    def validate_senha(cls, v):
        if v and len(v) < 1:
            raise ValueError('Senha é obrigatória')
        return v

class UsuarioResponse(BaseModel):
    id: int
    login: str
    email: str
    tag: str
    plan: Optional[str]
    plan_date: Optional[datetime]
    credencial: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Resposta do endpoint de login com JWT"""
    access_token: str
    token_type: str
    token_duration: int
    expires: int
    user: dict

class TokenData(BaseModel):
    """Dados extraídos do token JWT"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    login: Optional[str] = None
    tag: Optional[str] = None
    token_duration: Optional[str] = None
    token_version: Optional[str] = None

class CredentialValidation(BaseModel):
    """Validação de credencial gerada"""
    credencial: str
    is_unique: bool
    generated_at: datetime
    expires_at: datetime

class PasswordChangeRequest(BaseModel):
    """Request para alteração de senha"""
    senha_atual: str
    senha_nova: str
    confirmar_senha: str
    
    @validator('confirmar_senha')
    def validate_password_match(cls, v, values):
        if 'senha_nova' in values and v != values['senha_nova']:
            raise ValueError('Confirmação de senha não confere')
        return v
    
    @validator('senha_nova')
    def validate_new_password(cls, v):
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Nova senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres')
        return v
    
class TempKeyResponse(BaseModel):
    """Resposta do endpoint de tempkey"""
    tempkey: Optional[int] = None
    message: str
    email_sent: bool = False
    expires_in: Optional[str] = None
    warning: Optional[str] = None