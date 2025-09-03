from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db, criar_tabelas
from .schemas import UsuarioCreate, UsuarioResponse
from . import crud

app = FastAPI(title="BackBase API", version="1.0.0")

@app.on_event("startup")
def startup_event():
    """Executa na inicialização da aplicação"""
    criar_tabelas()

@app.post("/cadastro", response_model=dict)
def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário"""
    try:
        # Verifica se email já existe
        usuario_existente = crud.buscar_usuario_por_email(db, usuario.email)
        if usuario_existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        novo_usuario = crud.criar_usuario(db, usuario)
        return {
            "sucesso": True,
            "id": novo_usuario.id,
            "credencial": novo_usuario.credencial,
            "created_at": novo_usuario.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao cadastrar: {str(e)}")

@app.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    """Lista todos os usuários"""
    usuarios = crud.listar_usuarios(db)
    return usuarios

@app.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Busca um usuário por ID"""
    usuario = crud.buscar_usuario_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@app.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(usuario_id: int, dados: dict, db: Session = Depends(get_db)):
    """Atualiza dados de um usuário"""
    usuario = crud.atualizar_usuario(db, usuario_id, dados)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Deleta um usuário"""
    usuario = crud.deletar_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"sucesso": True, "mensagem": "Usuário deletado com sucesso"}

def main():
    print("FastAPI app configurado com sucesso!")