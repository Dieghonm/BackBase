from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import hashlib
import secrets

# Configurações JWT diretas para evitar import circular
SECRET_KEY = "dev-super-secret-key-change-in-production-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43800  # 🔥 1 MÊS = 30 dias * 24 horas * 60 minutos = 43,200 min + buffer

# Contexto para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        # 🔥 TOKEN DE 1 MÊS
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire.timestamp(),  # 🔧 CORRIGIDO: Usar timestamp() para epoch
        "iat": datetime.utcnow().timestamp(),  # 🔧 CORRIGIDO: Usar timestamp() para epoch
        "token_duration": "1_month"  # Identificador da duração
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        print(f"🎯 Token criado com expiração: {expire.strftime('%d/%m/%Y %H:%M:%S')} (1 mês)")
        print(f"🔧 Timestamp de expiração: {expire.timestamp()}")
        print(f"🔧 Timestamp atual: {datetime.utcnow().timestamp()}")
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
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 🔧 CORRIGIDO: Deixar a biblioteca python-jose fazer a validação de expiração
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Debug: Mostrar informações do token
        exp_timestamp = payload.get("exp")
        current_timestamp = datetime.utcnow().timestamp()
        
        print(f"🔧 Debug Token:")
        print(f"   - Token exp: {exp_timestamp}")
        print(f"   - Current: {current_timestamp}")
        print(f"   - Diff: {exp_timestamp - current_timestamp} segundos")
        
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            current_datetime = datetime.utcnow()
            print(f"   - Expira em: {exp_datetime}")
            print(f"   - Agora: {current_datetime}")
            print(f"   - Tempo restante: {exp_datetime - current_datetime}")
        
        # A biblioteca python-jose já faz a verificação de expiração automaticamente
        # Se chegou até aqui, o token está válido
        
        return payload
        
    except jwt.ExpiredSignatureError:
        print("❌ Token realmente expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado (1 mês se passou)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        print(f"❌ Erro JWT: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"❌ Erro geral: {e}")
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
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: user_id não encontrado"
        )
    
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "login": payload.get("login"),
        "tag": payload.get("tag"),
        "token_duration": payload.get("token_duration", "unknown")
    }

def hash_password(password: str) -> str:
    """
    Gera hash da senha usando bcrypt
    
    Args:
        password: Senha em texto plano
    
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha está correta
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha armazenada
    
    Returns:
        True se senha estiver correta
    """
    return pwd_context.verify(plain_password, hashed_password)

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

def gerar_credencial(email: str, dias: int = 365) -> str:  # 🔥 Credencial de 1 ano
    """Gera uma credencial única para o usuário (válida por 1 ano)"""
    validade = (datetime.utcnow() + timedelta(days=dias)).isoformat()
    raw = f"{email}-{validade}-{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()
