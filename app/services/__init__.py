# Imports de user_service
from .user_service import (
    criar_usuario,
    listar_usuarios,
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    buscar_usuario_por_login,
    atualizar_usuario,
    deletar_usuario,
    alterar_senha
)

# Import de auth_service  
from .auth_service import autenticar_usuario

# Para manter compatibilidade total com o código atual
# Agora você pode importar: from .services import criar_usuario, autenticar_usuario, etc.