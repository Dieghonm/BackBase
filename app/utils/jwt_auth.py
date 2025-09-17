from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from ..core.config import settings
# ✅ CORRIGIDO - agora importa apenas o que existe em security.py
from .security import hash_password, verify_password, gerar_credencial

ACCESS_TOKEN_EXPIRE_MINUTES = 43200
ACCESS_TOKEN_EXPIRE_SECONDS = 2592000

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT com duração de 1 MÊS
    
    Args:
        data: Dados para incluir no token (ex: user_id, email, tag)
        expires_delta: Tempo de expiração personalizado
    
    Returns:
        Token JWT como string (válido por 1 mês)
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_duration": "1_month",
        "token_version": "1.0"
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        print(f"🎯 Token criado com expiração: {expire.strftime('%d/%m/%Y %H:%M:%S')} (1 mês)")
        return encoded_jwt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar token: {str(e)}"
        )

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifica e decodifica um token JWT
    
    Args:
        token: Token JWT para verificar
    
    Returns:
        Payload do token decodificado
    
    Raises:
        HTTPException: Se token for inválido ou expirado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar token: {str(e)}"
        )

def get_user_from_token(token: str) -> Dict[str, Any]:
    """
    Extrai informações do usuário do token
    
    Args:
        token: Token JWT
    
    Returns:
        Dados do usuário do token
    """
    payload = verify_token(token)
    
    return {
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "login": payload.get("login"),
        "tag": payload.get("tag"),
        "token_duration": payload.get("token_duration", "1_month"),
        "token_version": payload.get("token_version", "1.0")
    }

def create_user_token_data(user_id: int, email: str, login: str, tag: str) -> Dict[str, Any]:
    """
    Cria os dados do usuário para incluir no token
    
    Args:
        user_id: ID do usuário
        email: Email do usuário  
        login: Login do usuário
        tag: Tag/role do usuário
    
    Returns:
        Dicionário com dados para o token
    """
    return {
        "user_id": user_id,
        "email": email,
        "login": login,
        "tag": tag,
        "token_type": "access",
        "created_at": datetime.utcnow().isoformat()
    }

class TokenResponse:
    """
    Resposta do endpoint de login com JWT (válido por 1 mês)
    Valores corrigidos para 30 dias exatos
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS  
    token_duration: str = "1_month"
    user: dict