from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from ..database.connection import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    tag = Column(String, nullable=False, default="cliente")
    plan = Column(String, nullable=True)
    plan_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    temp_senha = Column(String, nullable=True)
    temp_senha_expira = Column(DateTime, nullable=True)
    desejo_nome = Column(String, nullable=True)
    desejo_descricao = Column(String, nullable=True)
    sentimentos_selecionados = Column(JSON, nullable=True)
    caminho_selecionado = Column(String, nullable=True)
    teste_resultados = Column(JSON, nullable=True)