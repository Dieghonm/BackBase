from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db, criar_tabelas
from .schemas import UsuarioCreate, UsuarioResponse, LoginRequest
from . import crud

app = FastAPI(
    title="BackBase API", 
    version="1.0.0",
    description="API para gerenciamento de usuários",
    docs_url="/docs",
    redoc_url="/redoc"
)

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

# Rota raiz para health check
@app.get("/")
def root():
    """Endpoint raiz da API"""
    return {
        "message": "BackBase API está funcionando!",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
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

@app.post("/login", response_model=dict)
def fazer_login(dados_login: LoginRequest, db: Session = Depends(get_db)):
    """Realiza login do usuário"""
    try:
        # Busca usuário por email ou login
        usuario = crud.buscar_usuario_por_email(db, dados_login.email_ou_login)
        if not usuario:
            usuario = crud.buscar_usuario_por_login(db, dados_login.email_ou_login)
        
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        # Verifica senha (em produção, use hash)
        if usuario.senha != dados_login.senha:
            raise HTTPException(status_code=401, detail="Senha incorreta")
        
        return {
            "sucesso": True,
            "id": usuario.id,
            "login": usuario.login,
            "email": usuario.email,
            "tag": usuario.tag,
            "credencial": usuario.credencial,
            "message": "Login realizado com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer login: {str(e)}")

@app.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    """Lista todos os usuários"""
    try:
        usuarios = crud.listar_usuarios(db)
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")

@app.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Busca um usuário por ID"""
    try:
        usuario = crud.buscar_usuario_por_id(db, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")

@app.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(usuario_id: int, dados: dict, db: Session = Depends(get_db)):
    """Atualiza dados de um usuário"""
    try:
        usuario = crud.atualizar_usuario(db, usuario_id, dados)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Deleta um usuário"""
    try:
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