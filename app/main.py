from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .database import get_db, inicializar_banco
from .schemas.schemas import UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse, TempKeyResponse
from .core.config import settings
from .services.email_service import get_email_service

import random
from .utils.jwt_auth import (
    create_access_token, 
    get_user_from_token,
    create_user_token_data,
    hash_password,
    verify_password
)
from .services import (
    criar_usuario,
    listar_usuarios,    
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    buscar_usuario_por_login,
    atualizar_usuario,
)
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="BackBase API", 
    version="1.0.0",
    description="API para gerenciamento de usuários com JWT Authentication e Rate Limiting",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_safe,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

PLANOS = {
    "trial": 15,
    "mensal": 30,
    "trimestral": 90,
    "semestral": 180,
    "anual": 365,
    "admin": 36500,
}

def calcular_dias_restantes(usuario) -> int:
    """Calcula dias restantes do plano do usuário"""
    try:
        plan = usuario.plan.lower() if usuario.plan else "trial"
        plan_date = usuario.plan_date
        
        if not plan_date:
            return 0
        
        if plan not in PLANOS:
            return 0
        
        duracao = PLANOS[plan]
        fim = plan_date + timedelta(days=duracao)
        hoje = datetime.now()
        
        dias = (fim - hoje).days
        return max(dias, 0)
    except Exception as e:
        print(f"Erro ao calcular dias restantes: {e}")
        return 0

def obter_duracao_plano(usuario) -> int:
    """Retorna a duração total do plano em dias"""
    try:
        plan = usuario.plan.lower() if usuario.plan else "trial"
        return PLANOS.get(plan, 30)
    except Exception as e:
        print(f"Erro ao obter duração do plano: {e}")
        return 30

def gerar_token_para_usuario(usuario) -> str:
    """Cria e retorna um access token JWT para o usuário."""
    token_data = create_user_token_data(
        user_id=usuario.id,
        email=usuario.email,
        login=usuario.login,
        tag=usuario.tag
    )
    return create_access_token(data=token_data)

def montar_resposta_token(usuario, token: str) -> dict:
    """Monta a resposta padronizada com token e dados do usuário."""
    dias_restantes = calcular_dias_restantes(usuario)
    duracao_total = obter_duracao_plano(usuario)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "token_duration": duracao_total,
        "expires": dias_restantes,
        "user": {
            "login": usuario.login,
        }
    }

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    limit_value = str(exc.detail).split(" ")[0] if hasattr(exc, "detail") else "N/A"
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "message": "Muitas tentativas. Tente novamente mais tarde.",
            "limit": limit_value,
            "endpoint": str(request.url.path)
        },
        headers={"Retry-After": "60"}
    )

@app.on_event("startup")
def startup_event():
    """Executa na inicialização da aplicação"""
    inicializar_banco()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    DepEdency para verificar JWT e retornar usuário atual
    """
    token = credentials.credentials
    user_data = get_user_from_token(token)
    return user_data

@app.get("/")
def root():
    """Endpoint raiz da API"""
    return {
        "message": "BackBase API está funcionando!",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": ["JWT Authentication", "User Management", "Rate Limiting"],
        "rate_limits": {
            "login": settings.rate_limit_login,
            "cadastro": settings.rate_limit_cadastro
        }
    }

@app.get("/health")
def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "message": "API está funcionando corretamente",
        "rate_limiting": "ativo"
    }

@app.post("/cadastro", response_model=dict)
@limiter.limit(settings.rate_limit_cadastro)
def cadastrar_usuario(
    request: Request,
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """Cadastra um novo usuário (Rate Limit: 5/min)"""
    try:
        if buscar_usuario_por_email(db, usuario.email):
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        if buscar_usuario_por_login(db, usuario.login):
            raise HTTPException(status_code=400, detail="Login já está em uso")

        usuario.senha = hash_password(usuario.senha)
        novo_usuario = criar_usuario(db, usuario)

        try:
            email_service = get_email_service()
            if email_service:
                email_service.enviar_boas_vindas(
                    email=novo_usuario.email,
                    login=novo_usuario.login,
                    plan=novo_usuario.plan or "trial"
                )
        except Exception as e:
            print(f"⚠️  Erro ao enviar email: {str(e)}")

        token = gerar_token_para_usuario(novo_usuario)
        resposta = montar_resposta_token(novo_usuario, token)

        return {
            "sucesso": True,
            "message": "Usuário criado com sucesso",
            "created_at": novo_usuario.created_at,
            **resposta
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_login)
def fazer_login(
    request: Request,
    dados_login: LoginRequest,
    db: Session = Depends(get_db)
):
    """Endpoint de login com suporte a token renewal e credenciais"""
    
    try:
        usuario = None
        
        if dados_login.token:
            try:
                user_data = get_user_from_token(dados_login.token)
                usuario = buscar_usuario_por_id(db, user_data["user_id"])
                if not usuario:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Usuário não encontrado"
                    )

            except HTTPException as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e.detail)
                )
        else:
            usuario = buscar_usuario_por_email(db, dados_login.email_ou_login) \
                      or buscar_usuario_por_login(db, dados_login.email_ou_login)
            if not usuario:
                raise HTTPException(status_code=401, detail="Usuário não encontrado")

            if not verify_password(dados_login.senha, usuario.senha):
                raise HTTPException(status_code=401, detail="Senha incorreta")

        token = gerar_token_para_usuario(usuario)
        return montar_resposta_token(usuario, token)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao fazer login: {str(e)}"
        )

@app.get("/me")
def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retorna informações do usuário autenticado"""
    try:
        usuario = buscar_usuario_por_id(db, current_user["user_id"])
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        dias_restantes = calcular_dias_restantes(usuario)
        duracao_total = obter_duracao_plano(usuario)
        
        return {
            "id": usuario.id,
            "login": usuario.login,
            "email": usuario.email,
            "tag": usuario.tag,
            "plan": usuario.plan,
            "plan_date": usuario.plan_date,
            "token_duration": duracao_total,
            "expires": dias_restantes,
            "created_at": usuario.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")

@app.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios_endpoint(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lista todos os usuários (requer autenticação)"""
    try:
        if current_user["tag"] not in ["admin", "tester"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas admins podem listar usuários"
            )
        
        usuarios = listar_usuarios(db)
        return usuarios
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")
    
@app.post("/tempkey", response_model=dict)
@limiter.limit(settings.rate_limit_tempkey)
def recuperar_senha_endpoint(
    request: Request,
    dados_login: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de recuperação de senha - 3 estágios
    
    Estágio 1: Enviar email (email_ou_login apenas)
    Estágio 2: Validar código (email_ou_login + tempKey)
    Estágio 3: Alterar senha (email_ou_login + tempKey + new_password)
    
    Rate Limit: 10 requisições/hora
    """
    try:
        usuario = buscar_usuario_por_email(db, dados_login.email_ou_login) \
            or buscar_usuario_por_login(db, dados_login.email_ou_login)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )

        # ========== ESTÁGIO 1: ENVIAR EMAIL COM CÓDIGO ==========
        if not dados_login.tempKey and not dados_login.senha and not dados_login.new_password:
            print("📧 Estágio 1: Enviando email com código...")
            
            tempkey = str(random.randint(1000, 9999))
            hashKey = hash_password(tempkey)
            expires = datetime.utcnow() + timedelta(minutes=15)
            
            atualizar_usuario(
                db,
                usuario.id,
                {
                    'temp_senha': hashKey,
                    'temp_senha_expira': expires
                }
            )
            
            email_service = get_email_service()
            if not email_service:
                return {
                    "tempkey": tempkey,
                    "message": "BREVO_API_KEY não configurada no .env",
                    "email_sent": False,
                    "warning": "Configure BREVO_API_KEY para enviar emails",
                    "stage": 1
                }
            
            if not settings.email_enabled:
                return {
                    "tempkey": tempkey,
                    "message": "Serviço de email desabilitado",
                    "email_sent": False,
                    "stage": 1
                }
            
            email_enviado = email_service.enviar_tempkey(
                email=usuario.email,
                login=usuario.login,
                tempkey=tempkey
            )

            if email_enviado:
                return {
                    "tempkey": None,
                    "message": f"Código de recuperação enviado para {usuario.email}",
                    "email_sent": True,
                    "expires_in": "15 minutos",
                    "stage": 1
                }
            else:
                return {
                    "tempkey": tempkey,
                    "message": "Falha ao enviar email. Código exibido como fallback.",
                    "email_sent": False,
                    "warning": "Houve um problema ao enviar o email. Tente novamente.",
                    "stage": 1
                }

        # ========== ESTÁGIO 2: VALIDAR CÓDIGO (SEM nova senha) ==========
        elif dados_login.tempKey and not dados_login.new_password:
            print("✅ Estágio 2: Validando código...")
            
            if usuario.temp_senha and verify_password(str(dados_login.tempKey), usuario.temp_senha):
                if usuario.temp_senha_expira and datetime.utcnow() <= usuario.temp_senha_expira:
                    return {
                        "tempkey": dados_login.tempKey,
                        "message": "Código validado com sucesso",
                        "stage": 2,
                        "next_action": "Envie a nova senha no próximo request"
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Código expirado"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Código inválido"
                )

        # ========== ESTÁGIO 3: ALTERAR SENHA ==========
        elif dados_login.tempKey and dados_login.new_password:
            print("🔐 Estágio 3: Alterando senha...")
            print(f"Tempkey recebido: {dados_login.tempKey}")
            print(f"Nova senha recebida: {dados_login.new_password}")
            
            # Validar se o tempkey ainda existe
            if not usuario.temp_senha:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Nenhuma solicitação de recuperação ativa"
                )
            
            # Validar expiração
            if usuario.temp_senha_expira and datetime.utcnow() > usuario.temp_senha_expira:
                usuario.temp_senha = None
                usuario.temp_senha_expira = None
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Código expirado. Solicite um novo."
                )
            
            # Validar o tempkey
            if not verify_password(str(dados_login.tempKey), usuario.temp_senha):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Código inválido"
                )
            
            # ✅ Alterar a senha
            try:
                nova_senha_hash = hash_password(dados_login.new_password)
                
                usuario.senha = nova_senha_hash
                usuario.temp_senha = None
                usuario.temp_senha_expira = None
                
                db.commit()
                db.refresh(usuario)
                
                print("✅ Senha alterada com sucesso!")
                
                return {
                    "sucesso": True,
                    "message": "Senha alterada com sucesso! Faça login com sua nova senha.",
                    "email": usuario.email,
                    "updated_at": datetime.utcnow().isoformat(),
                    "stage": 3,
                    "next_action": "Faça login com suas novas credenciais"
                }
                
            except Exception as e:
                db.rollback()
                print(f"❌ Erro ao alterar senha: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao alterar senha: {str(e)}"
                )

    except HTTPException as e:
        print(f"\n❌ ERRO HTTP: {e.detail}")
        raise
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar recuperação de senha: {str(e)}"
        )

def main():
    print("FastAPI app configurado com sucesso!")
    print("✅ Rate Limiting ativo!")
