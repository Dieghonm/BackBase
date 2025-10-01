from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from ..core.config import settings

# Contexto de hash de senha (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Constantes de expiração
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 dias
ACCESS_TOKEN_EXPIRE_SECONDS = 2592000  # 30 dias em segundos


def hash_password(password: str) -> str:
    """
    Cria um hash seguro da senha usando bcrypt
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha como string
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash armazenado
    
    Args:
        password: Senha em texto plano fornecida pelo usuário
        hashed_password: Hash da senha armazenado no banco
        
    Returns:
        True se a senha estiver correta, False caso contrário
    """
    try:
        return pwd_context.verify(password, hashed_password)
    except Exception as e:
        print(f"Erro ao verificar senha: {e}")
        return False


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