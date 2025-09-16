import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Imports da aplicação
from app.main import app
from app.database.connection import Base
from app.database.session import get_db
from app.models.user import Usuario
from app.utils.jwt_auth import hash_password, create_access_token, create_user_token_data
from datetime import datetime

# ===== CONFIGURAÇÃO DO BANCO DE TESTE =====

# Criar banco de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===== FIXTURES =====

@pytest.fixture(scope="session")
def db_engine():
    """Engine do banco de dados para a sessão de teste"""
    return engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Sessão do banco de dados para cada teste"""
    # Criar todas as tabelas
    Base.metadata.create_all(bind=db_engine)
    
    # Criar sessão
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de teste do FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user_data():
    """Dados de usuário para testes"""
    return {
        "login": "testuserlogin",
        "senha": "TestPass123@",
        "email": "testuser@example.com",
        "tag": "cliente",
        "plan": "trial"
    }

@pytest.fixture
def admin_user_data():
    """Dados de usuário admin para testes"""
    return {
        "login": "admintest",
        "senha": "AdminPass123@",
        "email": "admin@example.com",
        "tag": "admin",
        "plan": "admin"
    }

@pytest.fixture
def created_user(db_session, sample_user_data):
    """Usuário já criado no banco para testes"""
    senha_hash = hash_password(sample_user_data["senha"])
    
    user = Usuario(
        login=sample_user_data["login"],
        senha=senha_hash,
        email=sample_user_data["email"],
        tag=sample_user_data["tag"],
        plan=sample_user_data["plan"],
        plan_date=datetime.utcnow() if sample_user_data["plan"] else None,
        credencial="test-credential-123",
        created_at=datetime.utcnow()
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user

@pytest.fixture
def created_admin_user(db_session, admin_user_data):
    """Usuário admin já criado no banco para testes"""
    senha_hash = hash_password(admin_user_data["senha"])
    
    admin = Usuario(
        login=admin_user_data["login"],
        senha=senha_hash,
        email=admin_user_data["email"],
        tag=admin_user_data["tag"],
        plan=admin_user_data["plan"],
        plan_date=datetime.utcnow(),
        credencial="admin-credential-123",
        created_at=datetime.utcnow()
    )
    
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    return admin

@pytest.fixture
def user_token(created_user):
    """Token JWT para usuário normal"""
    token_data = create_user_token_data(
        user_id=created_user.id,
        email=created_user.email,
        login=created_user.login,
        tag=created_user.tag
    )
    return create_access_token(data=token_data)

@pytest.fixture
def admin_token(created_admin_user):
    """Token JWT para usuário admin"""
    token_data = create_user_token_data(
        user_id=created_admin_user.id,
        email=created_admin_user.email,
        login=created_admin_user.login,
        tag=created_admin_user.tag
    )
    return create_access_token(data=token_data)

@pytest.fixture
def auth_headers(user_token):
    """Headers de autenticação para usuário normal"""
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def admin_auth_headers(admin_token):
    """Headers de autenticação para usuário admin"""
    return {"Authorization": f"Bearer {admin_token}"}

# ===== FIXTURES DE LIMPEZA =====

@pytest.fixture(autouse=True)
def clean_database(db_session):
    """Limpa o banco de dados antes de cada teste"""
    # Esta fixture é executada automaticamente antes de cada teste
    yield
    # Limpeza após o teste (se necessário)

# ===== CONFIGURAÇÕES PYTEST =====

def pytest_configure(config):
    """Configuração global do pytest"""
    # Configurar variáveis de ambiente para teste
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

def pytest_unconfigure(config):
    """Limpeza após todos os testes"""
    # Remover arquivo de banco de teste
    try:
        if os.path.exists("test.db"):
            os.remove("test.db")
    except:
        pass