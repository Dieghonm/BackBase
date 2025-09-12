from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db, criar_tabelas
from .schemas import UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse
from .utils.jwt_auth import (
    create_access_token, 
    verify_token, 
    get_user_from_token,
    create_user_token_data,
    hash_password,
    verify_password
)
from . import crud

app = FastAPI(
    title="BackBase API", 
    version="1.0.0",
    description="API para gerenciamento de usuários com JWT Authentication",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security scheme para JWT
security = HTTPBearer()

# Configuração CORS para produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Executa na inicialização da aplicação"""
    criar_tabelas()

# Dependency para verificar token JWT
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency para verificar JWT e retornar usuário atual
    """
    token = credentials.credentials
    user_data = get_user_from_token(token)
    return user_data

# Rota raiz para health check
@app.get("/")
def root():
    """Endpoint raiz da API"""
    return {
        "message": "BackBase API está funcionando!",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": ["JWT Authentication", "User Management"]
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "message": "API está funcionando corretamente"
    }

@app.post("/cadastro", response_model=dict)
def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário"""
    try:
        # Verifica se email já existe
        usuario_existente = crud.buscar_usuario_por_email(db, usuario.email)
        if usuario_existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        # Verifica se login já existe
        usuario_login_existente = crud.buscar_usuario_por_login(db, usuario.login)
        if usuario_login_existente:
            raise HTTPException(status_code=400, detail="Login já está em uso")
        
        # Hash da senha antes de salvar
        usuario.senha = hash_password(usuario.senha)
        
        novo_usuario = crud.criar_usuario(db, usuario)
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
def fazer_login(dados_login: LoginRequest, db: Session = Depends(get_db)):
    """Realiza login do usuário e retorna JWT"""
    try:
        # Busca usuário por email ou login
        usuario = crud.buscar_usuario_por_email(db, dados_login.email_ou_login)
        if not usuario:
            usuario = crud.buscar_usuario_por_login(db, dados_login.email_ou_login)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        # Verifica senha
        if not verify_password(dados_login.senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha incorreta"
            )
        
        # Cria dados do token
        token_data = create_user_token_data(
            user_id=usuario.id,
            email=usuario.email,
            login=usuario.login,
            tag=usuario.tag
        )
        
        # Gera JWT
        access_token = create_access_token(data=token_data)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutos
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
        usuario = crud.buscar_usuario_por_id(db, current_user["user_id"])
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
def listar_usuarios(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lista todos os usuários (requer autenticação)"""
    try:
        # Verifica se usuário tem permissão (admin)
        if current_user["tag"] not in ["admin", "tester"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas admins podem listar usuários"
            )
        
        usuarios = crud.listar_usuarios(db)
        return usuarios
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")

@app.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(usuario_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Busca um usuário por ID (requer autenticação)"""
    try:
        # Permite ver próprios dados ou se for admin
        if current_user["user_id"] != usuario_id and current_user["tag"] not in ["admin", "tester"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: você só pode ver seus próprios dados"
            )
        
        usuario = crud.buscar_usuario_por_id(db, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")

@app.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(usuario_id: int, dados: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atualiza dados de um usuário (requer autenticação)"""
    try:
        # Permite atualizar próprios dados ou se for admin
        if current_user["user_id"] != usuario_id and current_user["tag"] not in ["admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: você só pode atualizar seus próprios dados"
            )
        
        # Se for uma senha, faz hash
        if "senha" in dados:
            dados["senha"] = hash_password(dados["senha"])
        
        usuario = crud.atualizar_usuario(db, usuario_id, dados)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deleta um usuário (apenas admins)"""
    try:
        # Apenas admins podem deletar usuários
        if current_user["tag"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas admins podem deletar usuários"
            )
        
        usuario = crud.deletar_usuario(db, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return {"sucesso": True, "mensagem": "Usuário deletado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar usuário: {str(e)}")

def main():
    print("FastAPI app configurado com sucesso!")