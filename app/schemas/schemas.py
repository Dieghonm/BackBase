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
            raise ValueError('Login deve conter apenas letras, numeros e underscore')
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
    email_ou_login: Optional[str] = None
    tempKey: Optional[str] = None
    senha: Optional[str] = None
    token: Optional[str] = None
    new_password: Optional[str] = None  # ← ADICIONE ESTA LINHA
    
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
            raise ValueError('Senha eh obrigatoria')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if v and len(v) < 8:
            raise ValueError('Nova senha deve ter pelo menos 8 caracteres')
        return v
    
    @validator('token')
    def validate_inputs(cls, v, values):
        email_ou_login = values.get('email_ou_login')
        senha = values.get('senha')
        tempKey = values.get('tempKey')
        new_password = values.get('new_password')
        
        if v:
            if email_ou_login or senha or tempKey or new_password:
                raise ValueError('Forneca apenas TOKEN ou EMAIL SENHA ou EMAIL TEMPKEY')
            return v.strip()
        
        if tempKey is not None:
            if not email_ou_login:
                raise ValueError('Email ou login eh obrigatorio para validar tempKey')
            return v
        
        if email_ou_login and senha:
            return v
        
        raise ValueError('Forneca TOKEN ou EMAIL SENHA ou EMAIL TEMPKEY ou EMAIL TEMPKEY NEW_PASSWORD')



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
    access_token: str
    token_type: str
    token_duration: int
    expires: int
    user: dict

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    login: Optional[str] = None
    tag: Optional[str] = None
    token_duration: Optional[str] = None
    token_version: Optional[str] = None

class CredentialValidation(BaseModel):
    credencial: str
    is_unique: bool
    generated_at: datetime
    expires_at: datetime

class PasswordChangeRequest(BaseModel):
    senha_atual: str
    senha_nova: str
    confirmar_senha: str
    
    @validator('confirmar_senha')
    def validate_password_match(cls, v, values):
        if 'senha_nova' in values and v != values['senha_nova']:
            raise ValueError('Confirmacao de senha nao confere')
        return v
    
    @validator('senha_nova')
    def validate_new_password(cls, v):
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Nova senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres')
        return v

class PasswordRecoveryRequest(BaseModel):
    """Schema para a requisição de alteração de senha com tempKey"""
    email_ou_login: str
    tempKey: str
    new_password: str
    
    @validator('email_ou_login')
    def validate_email_ou_login(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Email ou login deve ter pelo menos 3 caracteres')
        return v.lower().strip()
    
    @validator('tempKey')
    def validate_tempkey(cls, v):
        if not v or len(v) != 4 or not v.isdigit():
            raise ValueError('TempKey deve ser um código de 4 dígitos')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres')
        return v


class PasswordRecoveryResponse(BaseModel):
    """Schema para a resposta de alteração de senha"""
    sucesso: bool
    message: str
    email: Optional[str] = None
    updated_at: Optional[datetime] = None
 
class TempKeyResponse(BaseModel):
    tempkey: Optional[str] = None
    message: str
    email_sent: bool = False
    expires_in: Optional[str] = None
    warning: Optional[str] = None