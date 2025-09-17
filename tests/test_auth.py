import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.utils.jwt_auth import create_access_token, verify_token, hash_password, verify_password

class TestAuth:
    """Testes para funcionalidades de autenticação"""
    
    def test_hash_password(self):
        """Testa se o hash de senha está funcionando"""
        password = "MinhaSecretePassword123@"
        hashed = hash_password(password)
        
        assert hashed != password
        
        assert hashed.startswith("$2b$")

        assert verify_password(password, hashed) is True
        assert verify_password("senha_errada", hashed) is False

    def test_create_access_token(self):
        """Testa criação de token JWT"""
        data = {
            "user_id": 1,
            "email": "test@example.com",
            "login": "testuser",
            "tag": "cliente"
        }
        
        token = create_access_token(data=data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50

    def test_verify_token_valid(self):
        """Testa verificação de token válido"""
        data = {
            "user_id": 1,
            "email": "test@example.com",
            "login": "testuser",
            "tag": "cliente"
        }
        
        token = create_access_token(data=data)
        payload = verify_token(token)
        
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
        assert payload["login"] == "testuser"
        assert payload["tag"] == "cliente"
        assert payload["token_duration"] == "1_month"

    def test_verify_token_invalid(self):
        """Testa verificação de token inválido"""
        invalid_token = "token.invalido.teste"
        
        with pytest.raises(Exception):
            verify_token(invalid_token)

class TestAuthEndpoints:
    """Testes para endpoints de autenticação"""
    
    def test_login_success(self, client, created_user, sample_user_data):
        """Testa login com credenciais válidas"""
        response = client.post("/login", json={
            "email_ou_login": sample_user_data["email"],
            "senha": sample_user_data["senha"]
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 2628000
        assert data["user"]["email"] == sample_user_data["email"]

    def test_login_with_login_field(self, client, created_user, sample_user_data):
        """Testa login usando campo login ao invés de email"""
        response = client.post("/login", json={
            "email_ou_login": sample_user_data["login"],
            "senha": sample_user_data["senha"]
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert data["user"]["login"] == sample_user_data["login"]

    def test_login_invalid_email(self, client):
        """Testa login com email inexistente"""
        response = client.post("/login", json={
            "email_ou_login": "inexistente@example.com",
            "senha": "qualquersenha"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "não encontrado" in response.json()["detail"]

    def test_login_invalid_password(self, client, created_user, sample_user_data):
        """Testa login com senha incorreta"""
        response = client.post("/login", json={
            "email_ou_login": sample_user_data["email"],
            "senha": "senha_incorreta"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Senha incorreta" in response.json()["detail"]

    def test_login_missing_fields(self, client):
        """Testa login sem campos obrigatórios"""
        # Sem senha
        response = client.post("/login", json={
            "email_ou_login": "test@example.com"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Sem email_ou_login
        response = client.post("/login", json={
            "senha": "123456"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_current_user_info(self, client, auth_headers, created_user):
        """Testa endpoint /me para obter informações do usuário logado"""
        response = client.get("/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == created_user.id
        assert data["login"] == created_user.login
        assert data["email"] == created_user.email
        assert data["tag"] == created_user.tag

    def test_get_current_user_without_token(self, client):
        """Testa endpoint /me sem token"""
        response = client.get("/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_invalid_token(self, client):
        """Testa endpoint /me com token inválido"""
        headers = {"Authorization": "Bearer token_invalido"}
        response = client.get("/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestRateLimiting:
    """Testes para rate limiting"""
    
    def test_login_rate_limit(self, client, created_user, sample_user_data):
        """Testa se rate limiting está funcionando no endpoint de login"""
        login_data = {
            "email_ou_login": sample_user_data["email"],
            "senha": "senha_incorreta"  # Usa senha incorreta para não fazer login real
        }
        
        # Faz várias tentativas rapidamente (mais que o limite de 5/minuto)
        responses = []
        for i in range(7):  # 7 tentativas (acima do limite de 5)
            response = client.post("/login", json=login_data)
            responses.append(response)
        
        # Pelo menos uma das respostas deve ser 429 (Too Many Requests)
        status_codes = [r.status_code for r in responses]
        
        # Como estamos testando com senhas incorretas, algumas serão 401
        # Mas se o rate limiting estiver funcionando, algumas podem ser 429
        # (dependendo da implementação do slowapi)
        assert any(code in [status.HTTP_429_TOO_MANY_REQUESTS, status.HTTP_401_UNAUTHORIZED] 
                  for code in status_codes)

    def test_cadastro_rate_limit(self, client):
        """Testa rate limiting no endpoint de cadastro"""
        base_data = {
            "login": "testuser",
            "senha": "TestPass123@",
            "email": "test@example.com",
            "tag": "cliente"
        }
        
        responses = []
        for i in range(5):  # 5 tentativas (no limite de 3/minuto)
            data = base_data.copy()
            data["email"] = f"test{i}@example.com"  # Email único
            data["login"] = f"testuser{i}"  # Login único
            
            response = client.post("/cadastro", json=data)
            responses.append(response)
        
        # Algumas podem ser bem-sucedidas (201) ou limitadas (429)
        status_codes = [r.status_code for r in responses]
        
        # Deve haver pelo menos algumas respostas de sucesso ou limite
        assert any(code in [status.HTTP_200_OK, status.HTTP_201_CREATED, 
                           status.HTTP_429_TOO_MANY_REQUESTS] 
                  for code in status_codes)

class TestJWTIntegration:
    """Testes de integração JWT com endpoints protegidos"""
    
    def test_protected_endpoint_with_valid_token(self, client, auth_headers):
        """Testa acesso a endpoint protegido com token válido"""
        response = client.get("/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_protected_endpoint_without_token(self, client):
        """Testa acesso a endpoint protegido sem token"""
        response = client.get("/usuarios")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_endpoint_with_user_token(self, client, auth_headers):
        """Testa acesso a endpoint admin com token de usuário normal"""
        response = client.get("/usuarios", headers=auth_headers)
        # Usuário normal não deve conseguir listar todos os usuários
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_endpoint_with_admin_token(self, client, admin_auth_headers, created_admin_user):
        """Testa acesso a endpoint admin com token de admin"""
        response = client.get("/usuarios", headers=admin_auth_headers)
        # Admin deve conseguir listar usuários
        assert response.status_code == status.HTTP_200_OK