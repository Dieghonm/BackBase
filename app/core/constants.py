"""
Constantes globais do BackBase API
Centraliza todas as opções válidas para manter consistência
"""

# ✅ TAGS DE USUÁRIO PADRONIZADAS
USER_TAGS = {
    'ADMIN': 'admin',
    'TESTER': 'tester', 
    'CLIENTE': 'cliente'  # ✅ Padronizado como 'cliente'
}

VALID_USER_TAGS = list(USER_TAGS.values())  # ['admin', 'tester', 'cliente']

# ✅ PLANS DISPONÍVEIS (SEM 'admin' que é tag, não plan)
USER_PLANS = {
    'TRIAL': 'trial',
    'MENSAL': 'mensal',
    'TRIMESTRAL': 'trimestral',
    'SEMESTRAL': 'semestral',
    'ANUAL': 'anual'
}

VALID_USER_PLANS = list(USER_PLANS.values())

# ✅ PLANS ESPECIAIS PARA SEEDS (admin pode ter plan diferente)
ADMIN_PLANS = ['admin', 'unlimited'] + VALID_USER_PLANS

# ✅ CONFIGURAÇÕES JWT CONSISTENTES
JWT_EXPIRE_DAYS = 30
JWT_EXPIRE_MINUTES = JWT_EXPIRE_DAYS * 24 * 60  # 43200 minutos
JWT_EXPIRE_SECONDS = JWT_EXPIRE_DAYS * 24 * 60 * 60  # 2,592,000 segundos

# ✅ CONFIGURAÇÕES DE SENHA CONSISTENTES
MIN_PASSWORD_LENGTH = 8  # ✅ Padrão único para todo o sistema

# ✅ RATE LIMITING
DEFAULT_RATE_LIMITS = {
    'LOGIN': '5/minute',
    'CADASTRO': '3/minute'
}