import pytest
from fastapi import status
import json

class TestHealthEndpoints:
    """Testes para endpoints de health check"""
    
    def test_root_endpoint(self, client):
        """Testa endpoint raiz /"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "BackBase API está funcionando!"
        assert data["status"] == "online"
        assert data["version"] == "1.0.0"
        assert "docs" in data
        assert "redoc" in data
        assert "features" in data
        assert "rate_limits" in data

    def test_health_endpoint(self, client):
        """Testa endpoint de health check"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
        assert "rate_limiting" in data

    def test_rate_limit_status_endpoint(self, client):
        """Testa endpoint de status do rate limiting"""
        response = client.get("/rate-limit-status")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "client_ip" in data
        assert "rate_limits" in data
        assert "message" in data
        assert "info" in data
        assert data["rate_limits"]["login"] == "5/minute"
        assert data["rate_limits"]["cadastro"] == "3/minute"

class TestCadastroEndpoint:
    """Testes detalhados para o endpoint de cadastro"""
    
    def test_cadastro_usuario_completo(self, client):
        """Testa cadastro com todos os campos preenchidos"""
        user_data = {
            "login": "usuariocompleto",
            "senha": "SenhaCompleta123@",
            "email": "completo@example.com",
            "tag": "tester",
            "plan": "semestral"
        }
        
        response = client.post("/cadastro", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["sucesso"] is True
        assert isinstance(data["id"], int)
        assert isinstance(data["credencial"], str)
        assert len(data["credencial"]) > 20  # Credencial deve ser longa
        assert "created_at" in data
        assert data["message"] == "Usuário criado com sucesso"

    def test_cadastro_usuario_minimo(self, client):
        """Testa cadastro com campos mínimos obrigatórios"""
        user_data = {
            "login": "userminimo",
            "senha": "SenhaMin123@",
            "email": "minimo@example.com"
            # tag e plan opcionais
        }
        
        response = client.post("/cadastro", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["sucesso"] is True

    def test_cadastro_diferentes_tags(self, client):
        """Testa cadastro com diferentes tipos de tag"""
        valid_tags = ["admin", "tester", "cliente", "usuario"]
        
        for i, tag in enumerate(valid_tags):
            user_data = {
                "login": f"user{tag}{i}",
                "senha": "ValidPass123@",
                "email": f"{tag}{i}@example.com",
                "tag": tag
            }
            
            response = client.post("/cadastro", json=user_data)
            assert response.status_code == status.HTTP_200_OK

    def test_cadastro_formato_resposta(self, client):
        """Testa formato exato da resposta do cadastro"""
        user_data = {
            "login": "userformat",
            "senha": "FormatPass123@",
            "email": "format@example.com",
            "tag": "cliente"
        }
        
        response = client.post("/cadastro", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        required_fields = ["sucesso", "id", "credencial", "created_at", "message"]
        
        for field in required_fields:
            assert field in data, f"Campo '{field}' não encontrado na resposta"
        
        # Verifica tipos
        assert isinstance(data["sucesso"], bool)
        assert isinstance(data["id"], int)
        assert isinstance(data["credencial"], str)
        assert isinstance(data["message"], str)

class TestLoginEndpoint:
    """Testes detalhados para o endpoint de login"""
    
    def test_login_formato_resposta(self, client, created_user, sample_user_data):
        """Testa formato exato da resposta do login"""
        response = client.post("/login", json={
            "email_ou_login": sample_user_data["email"],
            "senha": sample_user_data["senha"]
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        required_fields = ["access_token", "token_type", "expires_in", "token_duration", "user"]
        
        for field in required_fields:
            assert field in data, f"Campo '{field}' não encontrado na resposta"
        
        # Verifica tipos e valores específicos
        assert isinstance(data["access_token"], str)
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 2628000  # 1 mês em segundos
        assert data["token_duration"] == "1_month"
        assert isinstance(data["user"], dict)
        
        # Verifica campos do usuário
        user_fields = ["id", "login", "email", "tag", "credencial"]
        for field in user_fields:
            assert field in data["user"], f"Campo '{field}' não encontrado em user"

    def test_login_com_diferentes_formatos_email(self, client, created_user, sample_user_data):
        """Testa login com diferentes formatos de email"""
        # Email original
        response = client.post("/login", json={
            "email_ou_login": sample_user_data["email"],
            "senha": sample_user_data["senha"]
        })
        assert response.status_code == status.HTTP_200_OK
        
        # Email com maiúsculas
        response = client.post("/login", json={
            "email_ou_login": sample_user_data["email"].upper(),
            "senha": sample_user_data["senha"]
        })
        assert response.status_code == status.HTTP_200_OK
        
        # Email com espaços
        response = client.post("/login", json={
            "email_ou_login": f"  {sample_user_data['email']}  ",
            "senha": sample_user_data["senha"]
        })
        assert response.status_code == status.HTTP_200_OK

    def test_login_case_sensitivity_senha(self, client, created_user, sample_user_data):
        """Testa se senha é case-sensitive"""
        # Senha correta
        response = client.post("/login", json={
            "email_ou_login": sample_user_data["email"],
            "senha": sample_user_data["senha"]
        })
        assert response.status_code == status.HTTP_200_OK
        
        # Senha com case diferente (deve falhar)
        response = client.post("/login", json={
            "email_ou_login": sample_user_data["email"],
            "senha": sample_user_data["senha"].lower()
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestMeEndpoint:
    """Testes para endpoint /me"""
    
    def test_me_formato_resposta(self, client, auth_headers, created_user):
        """Testa formato da resposta do endpoint /me"""
        response = client.get("/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        required_fields = ["id", "login", "email", "tag", "plan", "created_at"]
        
        for field in required_fields:
            assert field in data, f"Campo '{field}' não encontrado na resposta"
        
        # Verifica se os dados correspondem ao usuário
        assert data["id"] == created_user.id
        assert data["login"] == created_user.login
        assert data["email"] == created_user.email
        assert data["tag"] == created_user.tag

    def test_me_sem_authorization_header(self, client):
        """Testa endpoint /me sem header Authorization"""
        response = client.get("/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_me_authorization_header_vazio(self, client):
        """Testa endpoint /me com header Authorization vazio"""
        headers = {"Authorization": ""}
        response = client.get("/me", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_me_bearer_sem_token(self, client):
        """Testa endpoint /me com Bearer mas sem token"""
        headers = {"Authorization": "Bearer "}
        response = client.get("/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestUsuariosListEndpoint:
    """Testes para endpoint GET /usuarios"""
    
    def test_listar_usuarios_como_admin_formato(self, client, admin_auth_headers, created_user, created_admin_user):
        """Testa formato da resposta de listagem como admin"""
        response = client.get("/usuarios", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Pelo menos os usuários criados
        
        # Verifica formato de cada usuário
        for usuario in data:
            required_fields = ["id", "login", "email", "tag", "plan", "plan_date", "credencial", "created_at"]
            for field in required_fields:
                assert field in usuario, f"Campo '{field}' não encontrado no usuário"

    def test_listar_usuarios_como_tester(self, client, created_user):
        """Testa listagem como tester (deve permitir)"""
        # Criar usuário tester
        tester_data = {
            "login": "testerteste",
            "senha": "TesterPass123@",
            "email": "tester@test.com",
            "tag": "tester"
        }
        
        cadastro_response = client.post("/cadastro", json=tester_data)
        assert cadastro_response.status_code == status.HTTP_200_OK
        
        # Fazer login como tester
        login_response = client.post("/login", json={
            "email_ou_login": "tester@test.com",
            "senha": "TesterPass123@"
        })
        assert login_response.status_code == status.HTTP_200_OK
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Listar usuários como tester
        response = client.get("/usuarios", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_listar_usuarios_permissoes_por_tag(self, client):
        """Testa permissões de listagem por diferentes tags"""
        # Criar usuários com diferentes tags
        test_users = [
            {"login": "cliente1", "email": "cliente1@test.com", "tag": "cliente", "senha": "Pass123@"},
            {"login": "usuario1", "email": "usuario1@test.com", "tag": "usuario", "senha": "Pass123@"}
        ]
        
        for user_data in test_users:
            # Cadastrar
            response = client.post("/cadastro", json=user_data)
            assert response.status_code == status.HTTP_200_OK
            
            # Fazer login
            login_response = client.post("/login", json={
                "email_ou_login": user_data["email"],
                "senha": user_data["senha"]
            })
            assert login_response.status_code == status.HTTP_200_OK
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Tentar listar usuários (deve falhar para cliente/usuario)
            response = client.get("/usuarios", headers=headers)
            assert response.status_code == status.HTTP_403_FORBIDDEN

class TestUsuarioIndividualEndpoint:
    """Testes para endpoint GET /usuarios/{id}"""
    
    def test_buscar_usuario_por_id_admin(self, client, admin_auth_headers, created_user):
        """Testa busca de usuário específico como admin"""
        response = client.get(f"/usuarios/{created_user.id}", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == created_user.id
        assert data["email"] == created_user.email

    def test_buscar_usuario_por_id_proprio(self, client, auth_headers, created_user):
        """Testa busca dos próprios dados"""
        response = client.get(f"/usuarios/{created_user.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == created_user.id

    def test_buscar_usuario_id_negativo(self, client, admin_auth_headers):
        """Testa busca com ID negativo"""
        response = client.get("/usuarios/-1", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_buscar_usuario_id_zero(self, client, admin_auth_headers):
        """Testa busca com ID zero"""
        response = client.get("/usuarios/0", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_buscar_usuario_id_string(self, client, admin_auth_headers):
        """Testa busca com ID como string"""
        response = client.get("/usuarios/abc", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestUpdateUsuarioEndpoint:
    """Testes para endpoint PUT /usuarios/{id}"""
    
    def test_atualizar_usuario_campos_permitidos(self, client, auth_headers, created_user):
        """Testa atualização com campos permitidos"""
        dados_atualizacao = {
            "login": "loginatualizado",
            "tag": "tester"
        }
        
        response = client.put(f"/usuarios/{created_user.id}", 
                             json=dados_atualizacao, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["login"] == "loginatualizado"
        assert data["tag"] == "tester"

    def test_atualizar_usuario_senha(self, client, auth_headers, created_user):
        """Testa atualização de senha"""
        dados_atualizacao = {
            "senha": "NovaSenha123@"
        }
        
        response = client.put(f"/usuarios/{created_user.id}", 
                             json=dados_atualizacao, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se consegue fazer login com nova senha
        login_response = client.post("/login", json={
            "email_ou_login": created_user.email,
            "senha": "NovaSenha123@"
        })
        assert login_response.status_code == status.HTTP_200_OK

    def test_atualizar_usuario_email_duplicado(self, client, auth_headers, created_user, created_admin_user):
        """Testa atualização com email que já existe"""
        dados_atualizacao = {
            "email": created_admin_user.email  # Email já existe
        }
        
        response = client.put(f"/usuarios/{created_user.id}", 
                             json=dados_atualizacao, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já está em uso" in response.json()["detail"]

class TestDeleteUsuarioEndpoint:
    """Testes para endpoint DELETE /usuarios/{id}"""
    
    def test_deletar_usuario_como_admin(self, client, admin_auth_headers):
        """Testa deleção de usuário como admin"""
        # Criar usuário para deletar
        user_data = {
            "login": "paradeletar",
            "senha": "DeletarPass123@",
            "email": "deletar@example.com",
            "tag": "cliente"
        }
        
        cadastro_response = client.post("/cadastro", json=user_data)
        assert cadastro_response.status_code == status.HTTP_200_OK
        
        user_id = cadastro_response.json()["id"]
        
        # Deletar usuário
        response = client.delete(f"/usuarios/{user_id}", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["sucesso"] is True
        assert "deletado com sucesso" in data["mensagem"]

    def test_deletar_usuario_inexistente(self, client, admin_auth_headers):
        """Testa deleção de usuário inexistente"""
        response = client.delete("/usuarios/99999", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "não encontrado" in response.json()["detail"]

    def test_deletar_sem_permissao(self, client, auth_headers, created_admin_user):
        """Testa deleção sem permissão de admin"""
        response = client.delete(f"/usuarios/{created_admin_user.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "apenas admins podem deletar" in response.json()["detail"]

class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_endpoint_inexistente(self, client):
        """Testa acesso a endpoint inexistente"""
        response = client.get("/endpoint/inexistente")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_metodo_nao_permitido(self, client):
        """Testa método HTTP não permitido"""
        # Tentar POST em endpoint que só aceita GET
        response = client.post("/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_json_malformado(self, client):
        """Testa requisição com JSON malformado"""
        import requests
        
        # Fazer requisição diretamente com JSON inválido
        response = client.post("/cadastro", 
                              data='{"login": "test", "senha": "test"',  # JSON incompleto
                              headers={"Content-Type": "application/json"})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_content_type_incorreto(self, client):
        """Testa requisição com Content-Type incorreto"""
        response = client.post("/cadastro", 
                              data="login=test&senha=test",  # Form data
                              headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
