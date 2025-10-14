from enum import Enum

# ============================================================================
# TAGS DE USUÁRIO (ROLES/PERMISSÕES)
# ============================================================================

class UserTag(str, Enum):
    """Enum para tags de usuário"""
    ADMIN = "admin"
    TESTER = "tester"
    CLIENTE = "cliente"

USER_TAGS = {
    'ADMIN': 'admin',
    'TESTER': 'tester', 
    'CLIENTE': 'cliente'
}

VALID_USER_TAGS = list(USER_TAGS.values())

# ============================================================================
# PLANOS DE USUÁRIO
# ============================================================================

class UserPlan(str, Enum):
    """Enum para planos de usuário"""
    TRIAL = "trial"
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"

USER_PLANS = {
    'TRIAL': 'trial',
    'MENSAL': 'mensal',
    'TRIMESTRAL': 'trimestral',
    'SEMESTRAL': 'semestral',
    'ANUAL': 'anual'
}
PLANS_TIME = {
    "trial": 15,
    "mensal": 30,
    "trimestral": 90,
    "semestral": 180,
    "anual": 365,
}

VALID_USER_PLANS = list(USER_PLANS.values())

# Planos especiais para administradores
ADMIN_PLANS = ['admin', 'unlimited'] + VALID_USER_PLANS

# ============================================================================
# CONFIGURAÇÕES DE JWT E AUTENTICAÇÃO
# ============================================================================

JWT_EXPIRE_DAYS = 30
JWT_EXPIRE_MINUTES = JWT_EXPIRE_DAYS * 24 * 60  # 30 dias em minutos
JWT_EXPIRE_SECONDS = JWT_EXPIRE_DAYS * 24 * 60 * 60  # 30 dias em segundos

# Configurações de senha
MIN_PASSWORD_LENGTH = 8

# ============================================================================
# RATE LIMITING
# ============================================================================

DEFAULT_RATE_LIMITS = {
    'LOGIN': '10/minute',
    'CADASTRO': '5/minute',
    'TEMPKEY': '4/hour'
}
