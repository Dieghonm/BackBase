"""
BACKBASE API - CONSTANTES GLOBAIS
==================================
Centraliza todas as constantes da aplicação para manter consistência
"""

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
    'CADASTRO': '5/minute'
}

# ============================================================================
# METADADOS DA API
# ============================================================================

API_METADATA = {
    "title": "BackBase API",
    "description": """
    ## 🚀 BackBase API - Sistema de Gerenciamento de Usuários
    
    API completa para gerenciamento de usuários com:
    
    - ✅ **Autenticação JWT** (válida por 30 dias)
    - ✅ **Rate Limiting** por IP
    - ✅ **Validações robustas** 
    - ✅ **Criptografia de senhas** (bcrypt)
    - ✅ **Controle de acesso** por tags
    - ✅ **Documentação interativa**
    
    ### 🏷️ Tags de Usuário
    - **admin**: Acesso total ao sistema
    - **tester**: Acesso para testes e validações
    - **cliente**: Usuário final com acesso limitado
    
    ### 📦 Planos Disponíveis
    - **trial**: Plano gratuito com limitações
    - **mensal**: Plano pago mensal
    - **trimestral**: Plano pago trimestral
    - **semestral**: Plano pago semestral
    - **anual**: Plano pago anual
    """,
    "version": "1.0.0"
}