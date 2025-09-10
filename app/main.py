from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db, criar_tabelas
from .schemas import UsuarioCreate, UsuarioResponse, LoginRequest
from . import crud
from pydantic import BaseModel

app = FastAPI(
    title="BackBase API", 
    version="1.0.0",
    description="API para gerenciamento de usuários com autenticação segura",
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

# Schema para alteração de senha
class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    senha_nova: str

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
        "redoc": "/redoc",
        "security": "Senhas criptografadas com bcrypt"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "message": "API está funcionando corretamente",
        "security": "✓ Criptografia ativa"
    }

@app.post("/cadastro", response_model=dict)
def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário com senha criptografada"""
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
            "login": novo_usuario.login,
            "email": novo_usuario.email,
            "credencial": novo_usuario.credencial,
            "created_at": novo_usuario.created_at,
            "message": "Usuário criado com sucesso (senha criptografada)"
        }
    except HTTPException:
        raise
    except ValueError as e:
        # Erros de validação do Pydantic
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/login", response_model=dict)
def fazer_login(dados_login: LoginRequest, db: Session = Depends(get_db)):
    """Realiza login do usuário com verificação segura da senha"""
    try:
        # Autentica o usuário usando a nova função segura
        usuario = crud.autenticar_usuario(db, dados_login.email_ou_login, dados_login.senha)
        
        if not usuario:
            raise HTTPException(
                status_code=401, 
                detail="Email/login ou senha incorretos"
            )
        
        return {
            "sucesso": True,
            "id": usuario.id,
            "login": usuario.login,
            "email": usuario.email,
            "tag": usuario.tag,
            "plan": usuario.plan,
            "credencial": usuario.credencial,
            "message": "Login realizado com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer login: {str(e)}")

@app.post("/alterar-senha/{usuario_id}")
def alterar_senha(
    usuario_id: int, 
    dados: AlterarSenhaRequest, 
    db: Session = Depends(get_db)
):
    """Altera a senha de um usuário após verificar a senha atual"""
    try:
        # Valida a nova senha
        from .utils.security import is_password_strong
        is_strong, errors = is_password_strong(dados.senha_nova)
        if not is_strong:
            raise HTTPException(
                status_code=400, 
                detail=f"Nova senha não atende aos critérios: {'; '.join(errors)}"
            )
        
        # Tenta alterar a senha
        sucesso = crud.alterar_senha(db, usuario_id, dados.senha_atual, dados.senha_nova)
        
        if not sucesso:
            raise HTTPException(
                status_code=400, 
                detail="Usuário não encontrado ou senha atual incorreta"
            )
        
        return {
            "sucesso": True,
            "message": "Senha alterada com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao alterar senha: {str(e)}")

@app.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    """Lista todos os usuários (sem mostrar senhas)"""
    try:
        usuarios = crud.listar_usuarios(db)
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")

@app.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Busca um usuário por ID (sem mostrar senha)"""
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
    """Atualiza dados de um usuário (senha será criptografada se fornecida)"""
    try:
        # Se senha está sendo atualizada, valida ela
        if 'senha' in dados:
            from .utils.security import is_password_strong
            is_strong, errors = is_password_strong(dados['senha'])
            if not is_strong:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Senha não atende aos critérios: {'; '.join(errors)}"
                )
        
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
    print("FastAPI app configurado com segurança de senhas!")