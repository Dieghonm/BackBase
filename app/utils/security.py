from passlib.context import CryptContext
import hashlib
import secrets
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Cria um hash seguro da senha usando bcrypt via passlib
    
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

def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """
    Verifica se a senha atende aos critérios de segurança
    
    Args:
        password: Senha a ser validada
        
    Returns:
        Tupla com (é_forte: bool, erros: list[str])
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Senha deve ter pelo menos 8 caracteres")
    
    if not any(c.islower() for c in password):
        errors.append("Senha deve ter pelo menos uma letra minúscula")
    
    if not any(c.isupper() for c in password):
        errors.append("Senha deve ter pelo menos uma letra maiúscula")
    
    if not any(c.isdigit() for c in password):
        errors.append("Senha deve ter pelo menos um número")

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Senha deve ter pelo menos um caractere especial")
    
    return len(errors) == 0, errors

# ✅ MOVIDO DE jwt_auth.py PARA CÁ - CORRIGE O IMPORT CIRCULAR
def gerar_credencial(email: str, dias: int = 365) -> str:
    """
    Gera uma credencial única para o usuário (válida por 1 ano)
    
    Args:
        email: Email do usuário
        dias: Validade em dias (padrão 365)
    
    Returns:
        Credencial SHA256 hexadecimal
    """
    validade = (datetime.utcnow() + timedelta(days=dias)).isoformat()
    raw = f"{email}-{validade}-{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()

def verify_credencial_uniqueness(db_session, credencial: str) -> bool:
    """
    Verifica se a credencial é única no banco de dados
    
    Args:
        db_session: Sessão do banco de dados
        credencial: Credencial a ser verificada
    
    Returns:
        True se credencial for única, False se já existir
    """
    from ..models.user import Usuario
    
    existing = db_session.query(Usuario).filter(Usuario.credencial == credencial).first()
    return existing is None