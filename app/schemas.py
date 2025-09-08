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