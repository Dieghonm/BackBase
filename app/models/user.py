from sqlalchemy import Column, Integer, String, DateTime
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