# app/main.py
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .schemas.schemas import ProgressoUpdate

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random
import traceback
from typing import Optional, List, Dict, Any

# Import local modules - adapte caminhos se necessário
from .database import get_db, inicializar_banco
from .schemas.schemas import (
    UsuarioCreate,
    UsuarioResponse,
    LoginRequest,
    TokenResponse,
    TempKeyResponse,
    StartingDataUpdate,
)
from .core.config import settings
from .services.email_service import get_email_service

from .utils.jwt_auth import (
    create_access_token,
    get_user_from_token,
    create_user_token_data,
    hash_password,
    verify_password,
)

from .services import (
    criar_usuario,
    listar_usuarios,
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    buscar_usuario_por_login,
    atualizar_usuario,
)

# -----------------------------
# Configurações e constantes
# -----------------------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="BackBase API",
    version="1.0.0",
    description="API para gerenciamento de usuários com JWT Authentication e Rate Limiting",
    docs_url="/docs",
    redoc_url="/redoc",
)

# rate limiter e middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_safe,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

security = HTTPBearer()

PLANOS = {
    "trial": 15,
    "mensal": 30,
    "trimestral": 90,
    "semestral": 180,
    "anual": 365,
    "admin": 36500,
}

# -----------------------------
# Helpers / Utils
# -----------------------------
def _safe_now() -> datetime:
    return datetime.utcnow()

def _get_plan_name(usuario) -> str:
    return (usuario.plan or "trial").lower()

def calcular_dias_restantes(usuario) -> int:
    """
    Calcula dias restantes do plano do usuário.
    Retorna 0 em caso de erro, plano desconhecido ou plan_date ausente.
    """
    try:
        plan = _get_plan_name(usuario)
        plan_date = usuario.plan_date
        if not plan_date or plan not in PLANOS:
            return 0
        fim = plan_date + timedelta(days=PLANOS[plan])
        dias = (fim - _safe_now()).days
        return max(dias, 0)
    except Exception:
        return 0

def obter_duracao_plano(usuario) -> int:
    """Retorna a duração total do plano em dias. Default: 30."""
    try:
        plan = _get_plan_name(usuario)
        return PLANOS.get(plan, 30)
    except Exception:
        return 30

def gerar_token_para_usuario(usuario) -> str:
    """Cria e retorna um access token JWT para o usuário."""
    token_data = create_user_token_data(
        user_id=usuario.id,
        email=usuario.email,
        login=usuario.login,
        tag=usuario.tag,
    )
    return create_access_token(data=token_data)

def montar_resposta_token(usuario, token: str) -> dict:
    """Monta a resposta padronizada com token e dados do usuário."""
    return {
        "access_token": token,
        "token_type": "bearer",
        "token_duration": obter_duracao_plano(usuario),
        "expires": calcular_dias_restantes(usuario),
        "user": {"login": usuario.login},
    }

# Usuário helpers
def get_usuario_by_email_or_login(db: Session, value: str):
    return buscar_usuario_por_email(db, value) or buscar_usuario_por_login(db, value)

def validar_usuario_existente(usuario):
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

def validar_senha(usuario, senha: str):
    if not verify_password(senha, usuario.senha):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta")

# Tempkey helpers
def gerar_tempkey() -> (str, str):
    """Gera tempkey e já retorna o hash dela."""
    tempkey = str(random.randint(1000, 9999))
    hash_key = hash_password(tempkey)
    return tempkey, hash_key

def validar_tempkey_completa(usuario, tempkey: str):
    """Valida existência, expiração e correspondência do tempkey. Levanta HTTPException quando inválido."""
    if not usuario.temp_senha:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nenhuma solicitação de recuperação ativa")

    if usuario.temp_senha_expira and _safe_now() > usuario.temp_senha_expira:
        # limpando campos expirados (persistência direta no DB não feita aqui para evitar acoplamento)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código expirado")

    if not verify_password(str(tempkey), usuario.temp_senha):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código inválido")

# -----------------------------
# Tratamento de exceções
# -----------------------------
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    limit_value = str(exc.detail).split(" ")[0] if hasattr(exc, "detail") else "N/A"
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "message": "Muitas tentativas. Tente novamente mais tarde.",
            "limit": limit_value,
            "endpoint": str(request.url.path),
        },
        headers={"Retry-After": "60"},
    )

# -----------------------------
# Startup
# -----------------------------
@app.on_event("startup")
def startup_event():
    """Executa na inicialização da aplicação"""
    inicializar_banco()

# -----------------------------
# Dependências
# -----------------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency para verificar JWT e retornar usuário atual (dados do token).
    Retorna o conteúdo do token (ex.: {'user_id': ..., ...})
    """
    token = credentials.credentials
    user_data = get_user_from_token(token)
    return user_data

# -----------------------------
# Endpoints públicos
# -----------------------------
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
        "rate_limits": {"login": settings.rate_limit_login, "cadastro": settings.rate_limit_cadastro},
    }

@app.get("/health")
def health_check():
    """Health check da API"""
    return {"status": "healthy", "message": "API está funcionando corretamente", "rate_limiting": "ativo"}

# -----------------------------
# Cadastro
# -----------------------------
@app.post("/cadastro", response_model=dict)
@limiter.limit(settings.rate_limit_cadastro)
def cadastrar_usuario(request: Request, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário (Rate Limit configurado em settings)"""
    try:
        if buscar_usuario_por_email(db, usuario.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")

        if buscar_usuario_por_login(db, usuario.login):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login já está em uso")

        usuario.senha = hash_password(usuario.senha)
        novo_usuario = criar_usuario(db, usuario)

        # Tenta enviar email de boas-vindas (não falha a rota caso dê erro no envio)
        try:
            email_service = get_email_service()
            if email_service:
                email_service.enviar_boas_vindas(
                    email=novo_usuario.email,
                    login=novo_usuario.login,
                    plan=novo_usuario.plan or "trial",
                )
        except Exception:
            # manter comportamento "soft-fail" do envio de email (log local)
            traceback.print_exc()

        token = gerar_token_para_usuario(novo_usuario)
        resposta = montar_resposta_token(novo_usuario, token)

        return {"sucesso": True, "message": "Usuário criado com sucesso", "created_at": novo_usuario.created_at, **resposta}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno: {str(e)}")

# -----------------------------
# Login
# -----------------------------
@app.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_login)
def fazer_login(request: Request, dados_login: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint de login com suporte a:
     - token (renovação) -> dados_login.token
     - credenciais (email/login + senha)
    """
    try:
        usuario = None

        # Renovação por token
        if getattr(dados_login, "token", None):
            try:
                user_data = get_user_from_token(dados_login.token)
                usuario = buscar_usuario_por_id(db, user_data["user_id"])
                if not usuario:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {str(e)}")
        else:
            usuario = get_usuario_by_email_or_login(db, dados_login.email_ou_login)
            validar_usuario_existente(usuario)
            validar_senha(usuario, dados_login.senha)

        token = gerar_token_para_usuario(usuario)
        return montar_resposta_token(usuario, token)

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao fazer login: {str(e)}")

# -----------------------------
# /me/starting - atualiza dados do "Starting"
# -----------------------------
@app.put("/me/starting", response_model=dict)
def atualizar_dados_starting(
    dados: StartingDataUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualiza os dados da jornada Starting do usuário.
    Campos opcionais — apenas os que vierem serão atualizados.
    """
    try:
        usuario = buscar_usuario_por_id(db, current_user["user_id"])
        validar_usuario_existente(usuario)

        fields = [
            "desejo_nome",
            "desejo_descricao",
            "sentimentos_selecionados",
            "caminho_selecionado",
            "teste_resultados",
        ]

        dados_atualizacao: Dict[str, Any] = {}
        for field in fields:
            if hasattr(dados, field):
                valor = getattr(dados, field)
                if valor is not None:
                    dados_atualizacao[field] = valor

        if dados_atualizacao:
            usuario_atualizado = atualizar_usuario(db, usuario.id, dados_atualizacao)
        else:
            usuario_atualizado = usuario  # nada a atualizar

        # Construindo resposta consistente
        resposta_dados = {
            "desejo_nome": usuario_atualizado.desejo_nome,
            "desejo_descricao": usuario_atualizado.desejo_descricao,
            "sentimentos_selecionados": usuario_atualizado.sentimentos_selecionados,
            "caminho_selecionado": usuario_atualizado.caminho_selecionado,
            "teste_resultados": usuario_atualizado.teste_resultados,
        }

        return {
            "sucesso": True,
            "message": "Dados da jornada atualizados com sucesso",
            "dados_atualizados": resposta_dados,
            "updated_at": _safe_now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao atualizar dados: {str(e)}")

# -----------------------------
# /me - informações do usuário autenticado
# -----------------------------
@app.get("/me", response_model=dict)
def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna informações completas do usuário autenticado"""
    try:
        usuario = buscar_usuario_por_id(db, current_user["user_id"])
        validar_usuario_existente(usuario)

        return {
            "id": usuario.id,
            "login": usuario.login,
            "email": usuario.email,
            "tag": usuario.tag,
            "plan": usuario.plan,
            "plan_date": usuario.plan_date,
            "token_duration": obter_duracao_plano(usuario),
            "expires": calcular_dias_restantes(usuario),
            "created_at": usuario.created_at,
            # Starting
            "desejo_nome": usuario.desejo_nome,
            "desejo_descricao": usuario.desejo_descricao,
            "sentimentos_selecionados": usuario.sentimentos_selecionados,
            "caminho_selecionado": usuario.caminho_selecionado,
            "teste_resultados": usuario.teste_resultados,
            # ✨ PROGRESSO (CAMPOS SEPARADOS)
            "semana_atual": usuario.semana_atual or 1,
            "dia_atual": usuario.dia_atual or 1,
            "progresso_atualizado_em": usuario.progresso_atualizado_em,
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar usuário: {str(e)}"
        )

@app.get("/me/progresso", response_model=dict)
def obter_progresso(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna o progresso atual do usuário na jornada.
    Usa campos separados: semana_atual, dia_atual, progresso_atualizado_em
    """
    try:
        usuario = buscar_usuario_por_id(db, current_user["user_id"])
        validar_usuario_existente(usuario)
        
        return {
            "sucesso": True,
            "progresso": {
                "semana_atual": usuario.semana_atual or 1,
                "dia_atual": usuario.dia_atual or 1,
                "progresso_atualizado_em": usuario.progresso_atualizado_em.isoformat() if usuario.progresso_atualizado_em else None,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter progresso: {str(e)}"
        )


@app.put("/me/progresso", response_model=dict)
def atualizar_progresso(
    dados: ProgressoUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza o progresso do usuário na jornada.
    Atualiza campos individuais: semana_atual e/ou dia_atual
    """
    try:
        usuario = buscar_usuario_por_id(db, current_user["user_id"])
        validar_usuario_existente(usuario)
        
        # Atualiza campos fornecidos
        campos_atualizados = {}
        
        if dados.semana_atual is not None:
            campos_atualizados["semana_atual"] = dados.semana_atual
        
        if dados.dia_atual is not None:
            campos_atualizados["dia_atual"] = dados.dia_atual
        
        # Sempre atualiza timestamp
        campos_atualizados["progresso_atualizado_em"] = datetime.utcnow()
        
        # Atualiza no banco
        usuario_atualizado = atualizar_usuario(db, usuario.id, campos_atualizados)
        
        return {
            "sucesso": True,
            "message": "Progresso atualizado com sucesso",
            "progresso": {
                "semana_atual": usuario_atualizado.semana_atual,
                "dia_atual": usuario_atualizado.dia_atual,
                "progresso_atualizado_em": usuario_atualizado.progresso_atualizado_em.isoformat() if usuario_atualizado.progresso_atualizado_em else None,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar progresso: {str(e)}"
        )


@app.post("/me/progresso/avancar", response_model=dict)
def avancar_dia(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Avança automaticamente para o próximo dia/semana.
    Semana 1-12, Dia 1-7.
    """
    try:
        usuario = buscar_usuario_por_id(db, current_user["user_id"])
        validar_usuario_existente(usuario)
        
        semana = usuario.semana_atual or 1
        dia = usuario.dia_atual or 1
        
        # Lógica de avanço
        if dia < 7:
            dia += 1
        elif semana < 12:
            semana += 1
            dia = 1
        else:
            # Jornada completa
            return {
                "sucesso": False,
                "message": "Jornada completa! Parabéns por concluir todas as 12 semanas!",
                "progresso": {
                    "semana_atual": semana,
                    "dia_atual": dia,
                    "progresso_atualizado_em": usuario.progresso_atualizado_em.isoformat() if usuario.progresso_atualizado_em else None,
                }
            }
        
        # Atualiza no banco
        campos_atualizados = {
            "semana_atual": semana,
            "dia_atual": dia,
            "progresso_atualizado_em": datetime.utcnow()
        }
        
        usuario_atualizado = atualizar_usuario(db, usuario.id, campos_atualizados)
        
        return {
            "sucesso": True,
            "message": f"Avançado para Semana {semana}, Dia {dia}",
            "progresso": {
                "semana_atual": usuario_atualizado.semana_atual,
                "dia_atual": usuario_atualizado.dia_atual,
                "progresso_atualizado_em": usuario_atualizado.progresso_atualizado_em.isoformat() if usuario_atualizado.progresso_atualizado_em else None,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao avançar progresso: {str(e)}"
        )


# -----------------------------
# Listar usuários (apenas admins/testers)
# -----------------------------
@app.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios_endpoint(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lista todos os usuários (requer autenticação e tag admin/tester)"""
    try:
        if current_user.get("tag") not in ["admin", "tester"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado: apenas admins podem listar usuários")

        usuarios = listar_usuarios(db)
        return usuarios
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao listar usuários: {str(e)}")

# -----------------------------
# Recuperação de senha (tempkey) - 3 estágios
# -----------------------------
@app.post("/tempkey", response_model=dict)
@limiter.limit(settings.rate_limit_tempkey)
def recuperar_senha_endpoint(request: Request, dados_login: LoginRequest, db: Session = Depends(get_db)):
    """
    Recuperação de senha em 3 estágios:
     1) Enviar email com código (email_ou_login)
     2) Validar código (email_ou_login + tempKey)
     3) Alterar senha (email_ou_login + tempKey + new_password)
    """
    try:
        usuario = get_usuario_by_email_or_login(db, dados_login.email_ou_login)
        validar_usuario_existente(usuario)

        # ---------- ESTÁGIO 1: ENVIAR CÓDIGO ----------
        if not getattr(dados_login, "tempKey", None) and not getattr(dados_login, "new_password", None):
            tempkey, hashKey = gerar_tempkey()
            expires = _safe_now() + timedelta(minutes=15)

            atualizar_usuario(db, usuario.id, {"temp_senha": hashKey, "temp_senha_expira": expires})

            email_service = get_email_service()
            # Se não houver serviço de email configurado ou desabilitado, retornamos o tempkey como fallback
            if not email_service or not settings.email_enabled:
                return {
                    "tempkey": tempkey,
                    "message": "Serviço de email não disponível. Código mostrado como fallback.",
                    "email_sent": False,
                    "stage": 1,
                }

            try:
                email_enviado = email_service.enviar_tempkey(email=usuario.email, login=usuario.login, tempkey=tempkey)
                if email_enviado:
                    return {"tempkey": None, "message": f"Código de recuperação enviado para {usuario.email}", "email_sent": True, "expires_in": "15 minutos", "stage": 1}
                else:
                    return {"tempkey": tempkey, "message": "Falha ao enviar email. Código exibido como fallback.", "email_sent": False, "stage": 1}
            except Exception:
                traceback.print_exc()
                return {"tempkey": tempkey, "message": "Erro ao enviar email. Código exibido como fallback.", "email_sent": False, "stage": 1}

        # ---------- ESTÁGIO 2: VALIDAR CÓDIGO ----------
        if getattr(dados_login, "tempKey", None) and not getattr(dados_login, "new_password", None):
            # verificar se o temp_senha existe e corresponde e se não expirou
            # validar_tempkey_completa levantará HTTPException se inválido
            if not usuario.temp_senha:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nenhuma solicitação de recuperação ativa")
            if usuario.temp_senha_expira and _safe_now() > usuario.temp_senha_expira:
                # limpar campos expirados
                usuario.temp_senha = None
                usuario.temp_senha_expira = None
                db.commit()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código expirado")
            if not verify_password(str(dados_login.tempKey), usuario.temp_senha):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código inválido")

            return {"tempkey": dados_login.tempKey, "message": "Código validado com sucesso", "stage": 2, "next_action": "Envie a nova senha no próximo request"}

        # ---------- ESTÁGIO 3: ALTERAR SENHA ----------
        if getattr(dados_login, "tempKey", None) and getattr(dados_login, "new_password", None):
            # validar existência e expiração
            if not usuario.temp_senha:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nenhuma solicitação de recuperação ativa")

            if usuario.temp_senha_expira and _safe_now() > usuario.temp_senha_expira:
                usuario.temp_senha = None
                usuario.temp_senha_expira = None
                db.commit()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código expirado. Solicite um novo.")

            if not verify_password(str(dados_login.tempKey), usuario.temp_senha):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código inválido")

            try:
                nova_senha_hash = hash_password(dados_login.new_password)
                usuario.senha = nova_senha_hash
                usuario.temp_senha = None
                usuario.temp_senha_expira = None
                db.commit()
                db.refresh(usuario)

                return {
                    "sucesso": True,
                    "message": "Senha alterada com sucesso! Faça login com sua nova senha.",
                    "email": usuario.email,
                    "updated_at": _safe_now().isoformat(),
                    "stage": 3,
                    "next_action": "Faça login com suas novas credenciais",
                }
            except Exception as e:
                db.rollback()
                traceback.print_exc()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao alterar senha: {str(e)}")

        # Se nenhum caso foi atendido
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requisição inválida para recuperação de senha")

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar recuperação de senha: {str(e)}")

# -----------------------------
# Main util (para execução local / debug)
# -----------------------------
def main():
    print("FastAPI app configurado com sucesso!")
    print("✅ Rate Limiting ativo!")

if __name__ == "__main__":
    main()

