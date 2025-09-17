"""
Constantes globais do BackBase API
Centraliza todas as opções válidas para manter consistência
"""

USER_TAGS = {
    'ADMIN': 'admin',
    'TESTER': 'tester', 
    'CLIENTE': 'cliente'
}

VALID_USER_TAGS = list(USER_TAGS.values())

USER_PLANS = {
    'TRIAL': 'trial',
    'MENSAL': 'mensal',
    'TRIMESTRAL': 'trimestral',
    'SEMESTRAL': 'semestral',
    'ANUAL': 'anual'
}

VALID_USER_PLANS = list(USER_PLANS.values())

ADMIN_PLANS = ['admin', 'unlimited'] + VALID_USER_PLANS

JWT_EXPIRE_DAYS = 30
JWT_EXPIRE_MINUTES = JWT_EXPIRE_DAYS * 24 * 60
JWT_EXPIRE_SECONDS = JWT_EXPIRE_DAYS * 24 * 60 * 60 

MIN_PASSWORD_LENGTH = 8

DEFAULT_RATE_LIMITS = {
    'LOGIN': '10/minute',
    'CADASTRO': '5/minute'
}