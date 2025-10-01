from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
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