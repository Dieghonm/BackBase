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
from .schemas.schemas import UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse
from .core.config import settings
from .utils.jwt_auth import (
    create_access_token, 
    verify_token, 
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
    deletar_usuario,
    autenticar_usuario
)
from datetime import datetime, timedelta

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
}

def dias_restantes(usuario):
    """Calcula dias restantes do plano do usuário"""
    plan = usuario.plan.lower()
    plan_date = usuario.plan_date

    if plan not in PLANOS:
        raise ValueError(f"Plano '{plan}' não é válido")

    duracao = PLANOS[plan]
    fim = plan_date + timedelta(days=duracao)
    hoje = datetime.now()

    dias = (fim - hoje).days
    return max(dias, 0)

def gerar_token_para_usuario(usuario) -> str:
    """Cria e retorna um access token JWT para o usuário."""
    token_data = create_user_token_data(
        user_id=usuario.id,
        email=usuario.email,
        login=usuario.login,
        tag=usuario.tag
    )
    return create_access_token(data=token_data)

def montar_resposta_token(usuario, token: str, timing, auth_method: str) -> dict:
    """Monta a resposta padronizada com token e dados do usuário."""
    return {
        "access_token": token,
        "timing": timing,
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
    print("🚦 Rate Limiting configurado:")
    print(f"   - Login: {settings.rate_limit_login}")
    print(f"   - Cadastro: {settings.rate_limit_cadastro}")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency para verificar JWT e retornar usuário atual
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
    """Cadastra um novo usuário (Rate Limit: 3/min)"""
    try:
        if buscar_usuario_por_email(db, usuario.email):
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        if buscar_usuario_por_login(db, usuario.login):
            raise HTTPException(status_code=400, detail="Login já está em uso")

        usuario.senha = hash_password(usuario.senha)
        novo_usuario = criar_usuario(db, usuario)

        timing = dias_restantes(novo_usuario)
        token = gerar_token_para_usuario(novo_usuario)
        resposta = montar_resposta_token(novo_usuario, token, timing, auth_method="registration")

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
        # Login via token (renewal)
        if dados_login.token:
            try:
                user_data = get_user_from_token(dados_login.token)
                usuario = buscar_usuario_por_id(db, user_data["user_id"])

                if not usuario:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Usuário não encontrado"
                    )

                timing = dias_restantes(usuario)
                token = gerar_token_para_usuario(usuario)
                return montar_resposta_token(usuario, token, timing, auth_method="token_renewal")

            except HTTPException as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e.detail)
                )

        # Login via credenciais (email/login + senha)
        usuario = buscar_usuario_por_email(db, dados_login.email_ou_login) \
                  or buscar_usuario_por_login(db, dados_login.email_ou_login)

        if not usuario:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")

        if not verify_password(dados_login.senha, usuario.senha):
            raise HTTPException(status_code=401, detail="Senha incorreta")

        timing = dias_restantes(usuario)
        token = gerar_token_para_usuario(usuario)
        return montar_resposta_token(usuario, token, timing, auth_method="credentials")

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
        
        return {
            "id": usuario.id,
            "login": usuario.login,
            "email": usuario.email,
            "tag": usuario.tag,
            "plan": usuario.plan,
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

def main():
    print("FastAPI app configurado com sucesso!")
    print("✅ Rate Limiting ativo!")