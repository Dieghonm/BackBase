import pytest
from fastapi import status
from app.models.user import Usuario
from app.services.user_service import (
    criar_usuario, 
    listar_usuarios, 
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    buscar_usuario_por_login,
    atualizar_usuario,
    deletar_usuario
)
from app.schemas.schemas import UsuarioCreate

class TestUserService:
    """Testes para os serviços de usuário (CRUD)"""
    
    def test_criar_usuario_success(self, db_session):
        """Testa criação de usuário com dados válidos"""
        user_data = UsuarioCreate(
            login="novouser",
            senha="NovaSenh@123",
            email="novouser@example.com",
            tag="cliente",
            plan="trial"
        )
        
        usuario = criar_usuario(db_session, user_data)
        
        assert usuario is not None
        assert usuario.login == "novouser"
        assert usuario.email == "novouser@example.com"
        assert usuario.tag == "cliente"
        assert usuario.plan == "trial"
        assert usuario.credencial is not None
        assert usuario.created_at is not None
        assert usuario.senha != "NovaSenh@123"
        assert usuario.senha.startswith("$2b$")

    def test_criar_usuario_email_duplicado(self, db_session, created_user, sample_user_data):
        """Testa criação de usuário com email duplicado"""
        user_data = UsuarioCreate(
            login="outrouser",
            senha="OutraSenha123@",
            email=sample_user_data["email"],
            tag="cliente"
        )
        
        with pytest.raises(Exception):
            criar_usuario(db_session, user_data)

    def test_criar_usuario_login_duplicado(self, db_session, created_user, sample_user_data):
        """Testa criação de usuário com login duplicado"""
        user_data = UsuarioCreate(
            login=sample_user_data["login"],
            senha="OutraSenha123@",
            email="outro@example.com",
            tag="cliente"
        )
        
        with pytest.raises(Exception):
            criar_usuario(db_session, user_data)

    def test_listar_usuarios(self, db_session, created_user, created_admin_user):
        """Testa listagem de usuários"""
        usuarios = listar_usuarios(db_session)
        
        assert len(usuarios) >= 2
        assert any(u.email == created_user.email for u in usuarios)
        assert any(u.email == created_admin_user.email for u in usuarios)

    def test_buscar_usuario_por_id_existente(self, db_session, created_user):
        """Testa busca de usuário por ID existente"""
        usuario = buscar_usuario_por_id(db_session, created_user.id)
        
        assert usuario is not None
        assert usuario.id == created_user.id
        assert usuario.email == created_user.email

    def test_buscar_usuario_por_id_inexistente(self, db_session):
        """Testa busca de usuário por ID inexistente"""
        usuario = buscar_usuario_por_id(db_session, 99999)
        
        assert usuario is None

    def test_buscar_usuario_por_email_existente(self, db_session, created_user):
        """Testa busca de usuário por email existente"""
        usuario = buscar_usuario_por_email(db_session, created_user.email)
        
        assert usuario is not None
        assert usuario.email == created_user.email

    def test_buscar_usuario_por_email_inexistente(self, db_session):
        """Testa busca de usuário por email inexistente"""
        usuario = buscar_usuario_por_email(db_session, "inexistente@example.com")
        
        assert usuario is None

    def test_buscar_usuario_por_login_existente(self, db_session, created_user):
        """Testa busca de usuário por login existente"""
        usuario = buscar_usuario_por_login(db_session, created_user.login)
        
        assert usuario is not None
        assert usuario.login == created_user.login

    def test_buscar_usuario_por_login_inexistente(self, db_session):
        """Testa busca de usuário por login inexistente"""
        usuario = buscar_usuario_por_login(db_session, "loginInexistente")
        
        assert usuario is None

    def test_atualizar_usuario_success(self, db_session, created_user):
        """Testa atualização de usuário com dados válidos"""
        novos_dados = {
            "login": "loginAtualizado",
            "tag": "tester"
        }
        
        usuario_atualizado = atualizar_usuario(db_session, created_user.id, novos_dados)
        
        assert usuario_atualizado is not None
        assert usuario_atualizado.login == "loginatualizado"
        assert usuario_atualizado.tag == "tester"
        assert usuario_atualizado.email == created_user.email 

    def test_atualizar_usuario_inexistente(self, db_session):
        """Testa atualização de usuário inexistente"""
        novos_dados = {"tag": "admin"}
        
        usuario = atualizar_usuario(db_session, 99999, novos_dados)
        
        assert usuario is None

    def test_deletar_usuario_existente(self, db_session, created_user):
        """Testa deleção de usuário existente"""
        user_id = created_user.id
        
        usuario_deletado = deletar_usuario(db_session, user_id)
        
        assert usuario_deletado is not None
        assert usuario_deletado.id == user_id
        
        usuario_busca = buscar_usuario_por_id(db_session, user_id)
        assert usuario_busca is None

    def test_deletar_usuario_inexistente(self, db_session):
        """Testa deleção de usuário inexistente"""
        usuario = deletar_usuario(db_session, 99999)
        
        assert usuario is None

class TestUserEndpoints:
    """Testes para endpoints de usuários"""
    
    def test_cadastro_usuario_success(self, client):
        """Testa cadastro de usuário via endpoint"""
        user_data = {
            "login": "novoUsuarioAPI",
            "senha": "SenhaSegura123@",
            "email": "novo@api.com",
            "tag": "cliente",
            "plan": "mensal"
        }
        
        response = client.post("/cadastro", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["sucesso"] is True
        assert "id" in data
        assert "credencial" in data
        assert "created_at" in data
        assert data["message"] == "Usuário criado com sucesso"

    def test_cadastro_usuario_email_duplicado(self, client, created_user):
        """Testa cadastro com email duplicado via endpoint"""
        user_data = {
            "login": "outroLogin",
            "senha": "SenhaSegura123@",
            "email": created_user.email,
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já cadastrado" in response.json()["detail"]

    def test_cadastro_usuario_dados_invalidos(self, client):
        """Testa cadastro com dados inválidos"""
        user_data = {
            "login": "test",
            "senha": "123",
            "email": "test@example.com",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        user_data = {
            "login": "validuser",
            "senha": "ValidPass123@",
            "email": "email-invalido",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_listar_usuarios_como_admin(self, client, admin_auth_headers, created_user, created_admin_user):
        """Testa listagem de usuários como admin"""
        response = client.get("/usuarios", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_listar_usuarios_como_usuario_normal(self, client, auth_headers):
        """Testa listagem de usuários como usuário normal (deve falhar)"""
        response = client.get("/usuarios", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "admins podem listar" in response.json()["detail"]

    def test_listar_usuarios_sem_auth(self, client):
        """Testa listagem de usuários sem autenticação"""
        response = client.get("/usuarios")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_buscar_usuario_proprio(self, client, auth_headers, created_user):
        """Testa busca dos próprios dados do usuário"""
        response = client.get(f"/usuarios/{created_user.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == created_user.id
        assert data["email"] == created_user.email

    def test_buscar_usuario_outro_como_user_normal(self, client, auth_headers, created_admin_user):
        """Testa busca de dados de outro usuário como usuário normal (deve falhar)"""
        response = client.get(f"/usuarios/{created_admin_user.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "seus próprios dados" in response.json()["detail"]

    def test_buscar_usuario_como_admin(self, client, admin_auth_headers, created_user):
        """Testa busca de dados de qualquer usuário como admin"""
        response = client.get(f"/usuarios/{created_user.id}", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == created_user.id

    def test_buscar_usuario_inexistente(self, client, admin_auth_headers):
        """Testa busca de usuário inexistente"""
        response = client.get("/usuarios/99999", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "não encontrado" in response.json()["detail"]

    def test_atualizar_usuario_proprio(self, client, auth_headers, created_user):
        """Testa atualização dos próprios dados"""
        novos_dados = {
            "tag": "tester"
        }
        
        response = client.put(f"/usuarios/{created_user.id}", 
                             json=novos_dados, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["tag"] == "tester"

    def test_atualizar_outro_usuario_como_normal(self, client, auth_headers, created_admin_user):
        """Testa atualização de outro usuário como usuário normal (deve falhar)"""
        novos_dados = {"tag": "admin"}
        
        response = client.put(f"/usuarios/{created_admin_user.id}", 
                             json=novos_dados, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_deletar_usuario_como_admin(self, client, admin_auth_headers, created_user):
        """Testa deleção de usuário como admin"""
        response = client.delete(f"/usuarios/{created_user.id}", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["sucesso"] is True
        assert "deletado com sucesso" in data["mensagem"]

    def test_deletar_usuario_como_normal(self, client, auth_headers, created_admin_user):
        """Testa deleção de usuário como usuário normal (deve falhar)"""
        response = client.delete(f"/usuarios/{created_admin_user.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "apenas admins podem deletar" in response.json()["detail"]

    def test_deletar_usuario_inexistente(self, client, admin_auth_headers):
        """Testa deleção de usuário inexistente"""
        response = client.delete("/usuarios/99999", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "não encontrado" in response.json()["detail"]

class TestUserValidation:
    """Testes para validações específicas de usuário"""
    
    def test_login_validation_minimo_caracteres(self, client):
        """Testa validação de login com poucos caracteres"""
        user_data = {
            "login": "ab",
            "senha": "ValidPass123@",
            "email": "test@example.com",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_validation_caracteres_especiais(self, client):
        """Testa validação de login com caracteres especiais inválidos"""
        user_data = {
            "login": "user@test",
            "senha": "ValidPass123@",
            "email": "test@example.com",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_email_validation_formato_invalido(self, client):
        """Testa validação de email com formato inválido"""
        user_data = {
            "login": "validuser",
            "senha": "ValidPass123@",
            "email": "email.invalido",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_tag_validation_valor_invalido(self, client):
        """Testa validação de tag com valor inválido"""
        user_data = {
            "login": "validuser",
            "senha": "ValidPass123@",
            "email": "test@example.com",
            "tag": "tag_invalida"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_plan_validation_valor_invalido(self, client):
        """Testa validação de plan com valor inválido"""
        user_data = {
            "login": "validuser",
            "senha": "ValidPass123@",
            "email": "test@example.com",
            "tag": "cliente",
            "plan": "plan_invalido"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_senha_validation_muito_curta(self, client):
        """Testa validação de senha muito curta"""
        user_data = {
            "login": "validuser",
            "senha": "123",
            "email": "test@example.com",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestUserEdgeCases:
    """Testes para casos extremos e edge cases"""
    
    def test_criar_usuario_email_maiusculo(self, client):
        """Testa criação de usuário com email em maiúsculo (deve converter para minúsculo)"""
        user_data = {
            "login": "testuser",
            "senha": "ValidPass123@",
            "email": "TEST@EXAMPLE.COM",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_200_OK
        
        login_response = client.post("/login", json={
            "email_ou_login": "test@example.com",
            "senha": "ValidPass123@"
        })
        assert login_response.status_code == status.HTTP_200_OK

    def test_criar_usuario_login_maiusculo(self, client):
        """Testa criação de usuário com login em maiúsculo (deve converter para minúsculo)"""
        user_data = {
            "login": "TESTUSER",
            "senha": "ValidPass123@",
            "email": "test@example.com",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_200_OK
        
        login_response = client.post("/login", json={
            "email_ou_login": "testuser",
            "senha": "ValidPass123@"
        })
        assert login_response.status_code == status.HTTP_200_OK

    def test_plan_opcional_none(self, client):
        """Testa criação de usuário sem plan (deve aceitar None)"""
        user_data = {
            "login": "usernoplan",
            "senha": "ValidPass123@",
            "email": "noplan@example.com",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        assert response.status_code == status.HTTP_200_OK