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
def cadastrar_usuario(request: Request, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário (Rate Limit: 3 tentativas por minuto)"""
    try:
        usuario_existente = buscar_usuario_por_email(db, usuario.email)
        if usuario_existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        usuario_login_existente = buscar_usuario_por_login(db, usuario.login)
        if usuario_login_existente:
            raise HTTPException(status_code=400, detail="Login já está em uso")
        
        usuario.senha = hash_password(usuario.senha)
        
        novo_usuario = criar_usuario(db, usuario)
        return {
            "sucesso": True,
            "id": novo_usuario.id,
            "credencial": novo_usuario.credencial,
            "created_at": novo_usuario.created_at,
            "message": "Usuário criado com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_login)
def fazer_login(request: Request, dados_login: LoginRequest, db: Session = Depends(get_db)):
    """Realiza login do usuário e retorna JWT (VÁLIDO POR 1 MÊS)"""
    try:
        usuario = buscar_usuario_por_email(db, dados_login.email_ou_login)
        if not usuario:
            usuario = buscar_usuario_por_login(db, dados_login.email_ou_login)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        if not verify_password(dados_login.senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha incorreta"
            )
        
        token_data = create_user_token_data(
            user_id=usuario.id,
            email=usuario.email,
            login=usuario.login,
            tag=usuario.tag
        )
        
        access_token = create_access_token(data=token_data)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=2628000,
            token_duration="1_month",
            user={
                "id": usuario.id,
                "login": usuario.login,
                "email": usuario.email,
                "tag": usuario.tag,
                "credencial": usuario.credencial
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer login: {str(e)}")

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

@app.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario_endpoint(usuario_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Busca um usuário por ID (requer autenticação)"""
    try:
        if current_user["user_id"] != usuario_id and current_user["tag"] not in ["admin", "tester"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: você só pode ver seus próprios dados"
            )
        
        usuario = buscar_usuario_por_id(db, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")

@app.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario_endpoint(usuario_id: int, dados: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atualiza dados de um usuário (requer autenticação)"""
    try:
        if current_user["user_id"] != usuario_id and current_user["tag"] not in ["admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: você só pode atualizar seus próprios dados"
            )
        
        if "senha" in dados:
            dados["senha"] = hash_password(dados["senha"])
        
        usuario = atualizar_usuario(db, usuario_id, dados)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

@app.delete("/usuarios/{usuario_id}")
def deletar_usuario_endpoint(usuario_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deleta um usuário (apenas admins)"""
    try:
        if current_user["tag"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas admins podem deletar usuários"
            )
        
        usuario = deletar_usuario(db, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return {"sucesso": True, "mensagem": "Usuário deletado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar usuário: {str(e)}")

@app.get("/rate-limit-status")
def get_rate_limit_status(request: Request):
    """Endpoint para verificar status atual do rate limiting"""
    client_ip = get_remote_address(request)
    return {
        "client_ip": client_ip,
        "rate_limits": {
            "login": settings.rate_limit_login,
            "cadastro": settings.rate_limit_cadastro
        },
        "message": "Rate limiting está ativo",
        "info": "As limitações se aplicam por IP address"
    }

def main():
    print("FastAPI app configurado com sucesso!")
    print("✅ Rate Limiting ativo!")