from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from ..core.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

Base = declarative_base()