import bcrypt

def hash_password(password: str) -> str:
    """
    Cria um hash seguro da senha usando bcrypt
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha como string
    """
    # Converte a senha para bytes
    password_bytes = password.encode('utf-8')
    
    # Gera um salt e cria o hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Retorna o hash como string
    return hashed.decode('utf-8')

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
        # Converte ambos para bytes
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Verifica se a senha corresponde ao hash
        return bcrypt.checkpw(password_bytes, hashed_bytes)
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
    
    # Verifica comprimento mínimo
    if len(password) < 8:
        errors.append("Senha deve ter pelo menos 8 caracteres")
    
    # Verifica se tem pelo menos uma letra minúscula
    if not any(c.islower() for c in password):
        errors.append("Senha deve ter pelo menos uma letra minúscula")
    
    # Verifica se tem pelo menos uma letra maiúscula
    if not any(c.isupper() for c in password):
        errors.append("Senha deve ter pelo menos uma letra maiúscula")
    
    # Verifica se tem pelo menos um número
    if not any(c.isdigit() for c in password):
        errors.append("Senha deve ter pelo menos um número")
    
    # Verifica se tem pelo menos um caractere especial
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Senha deve ter pelo menos um caractere especial")
    
    return len(errors) == 0, errors

