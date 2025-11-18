from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List, Dict
from ..core.constants import VALID_USER_TAGS, VALID_USER_PLANS, MIN_PASSWORD_LENGTH

class UsuarioCreate(BaseModel):
    login: str
    senha: str
    email: EmailStr
    tag: str = "cliente"
    plan: Optional[str] = None
    
    @validator('login')
    def validate_login(cls, v):
        if len(v) < 4 or len(v) > 20:
            raise ValueError('Login deve ter entre 4 e 20 caracteres')
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


# ✨ NOVO SCHEMA PARA ATUALIZAR DADOS DO STARTING
class StartingDataUpdate(BaseModel):
    """Schema para atualizar dados da jornada Starting"""
    desejo_nome: Optional[str] = None
    desejo_descricao: Optional[str] = None
    sentimentos_selecionados: Optional[List[int]] = None
    caminho_selecionado: Optional[str] = None
    teste_resultados: Optional[Dict[str, float]] = None
    
    @validator('desejo_nome')
    def validate_desejo_nome(cls, v):
        if v and len(v) > 15:
            raise ValueError('Nome do desejo deve ter no máximo 15 caracteres')
        return v.strip() if v else None
    
    @validator('desejo_descricao')
    def validate_desejo_descricao(cls, v):
        if v and len(v) > 300:
            raise ValueError('Descrição do desejo deve ter no máximo 300 caracteres')
        return v.strip() if v else None
    
    @validator('sentimentos_selecionados')
    def validate_sentimentos(cls, v):
        if v and len(v) != 3:
            raise ValueError('Devem ser selecionados exatamente 3 sentimentos')
        if v and not all(1 <= s <= 5 for s in v):
            raise ValueError('IDs de sentimentos devem estar entre 1 e 5')
        return v
    
    @validator('caminho_selecionado')
    def validate_caminho(cls, v):
        caminhos_validos = ['Ansiedade', 'Autoimagem', 'Atenção Plena', 'Motivação', 'Relacionamentos']
        if v and v not in caminhos_validos:
            raise ValueError(f'Caminho deve ser um de: {", ".join(caminhos_validos)}')
        return v
    
    @validator('teste_resultados')
    def validate_teste_resultados(cls, v):
        if v:
            # Validar que as porcentagens somam ~100%
            total = sum(v.values())
            if not (99 <= total <= 101):  # Margem de erro de 1%
                raise ValueError('Porcentagens devem somar aproximadamente 100%')
        return v


class LoginRequest(BaseModel):
    email_ou_login: Optional[str] = None
    tempKey: Optional[str] = None
    senha: Optional[str] = None
    token: Optional[str] = None
    new_password: Optional[str] = None
    
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
    created_at: datetime
    
    # ✨ NOVOS CAMPOS NA RESPOSTA
    desejo_nome: Optional[str] = None
    desejo_descricao: Optional[str] = None
    sentimentos_selecionados: Optional[List[int]] = None
    caminho_selecionado: Optional[str] = None
    teste_resultados: Optional[Dict[str, float]] = None

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