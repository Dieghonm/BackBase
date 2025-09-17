import pytest
import time
import concurrent.futures
from fastapi import status

class TestPerformanceBasic:
    """Testes básicos de performance"""
    
    def test_tempo_resposta_health_check(self, client):
        """Testa se health check responde rapidamente"""
        start_time = time.time()
        
        response = client.get("/health")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0, f"Rate limiting afetou performance normal: {response_time:.3f}s"

    def test_rate_limit_response_time(self, client):
        """Testa tempo de resposta quando rate limit é ativado"""
        responses = []
        times = []
        
        for i in range(8):
            start_time = time.time()
            
            try:
                response = client.get("/rate-limit-status")
                end_time = time.time()
                response_time = end_time - start_time
                
                responses.append(response.status_code)
                times.append(response_time)
                
            except Exception:
                continue
        
        for response_time in times:
            assert response_time < 2.0, f"Rate limit response muito lento: {response_time:.3f}s"

class TestPerformanceBenchmarks:
    """Benchmarks de performance para comparação"""
    
    def test_benchmark_operacoes_basicas(self, client, created_user, sample_user_data, auth_headers):
        """Benchmark de operações básicas da API"""
        benchmarks = {}
        
        start = time.time()
        response = client.get("/health")
        benchmarks["health_check"] = time.time() - start
        assert response.status_code == status.HTTP_200_OK
        
        start = time.time()
        response = client.post("/login", json={
            "email_ou_login": sample_user_data["email"],
            "senha": sample_user_data["senha"]
        })
        benchmarks["login"] = time.time() - start
        assert response.status_code == status.HTTP_200_OK
        
        start = time.time()
        response = client.get("/me", headers=auth_headers)
        benchmarks["get_user_info"] = time.time() - start
        assert response.status_code == status.HTTP_200_OK
        
        start = time.time()
        response = client.get(f"/usuarios/{created_user.id}", headers=auth_headers)
        benchmarks["get_user_by_id"] = time.time() - start
        assert response.status_code == status.HTTP_200_OK
        
        print(f"\n📊 BENCHMARKS DE PERFORMANCE:")
        for operation, time_taken in benchmarks.items():
            print(f"   - {operation}: {time_taken:.3f}s")
        
        assert benchmarks["health_check"] < 0.5, "Health check muito lento"
        assert benchmarks["login"] < 2.0, "Login muito lento"  
        assert benchmarks["get_user_info"] < 1.0, "Get user info muito lento"
        assert benchmarks["get_user_by_id"] < 1.0, "Get user by ID muito lento"
        
        avg_time = sum(benchmarks.values()) / len(benchmarks)
        assert avg_time < 1.0, f"Tempo médio muito alto: {avg_time:.3f}s"

    def test_benchmark_crud_completo(self, client):
        """Benchmark de um CRUD completo de usuário"""
        total_start = time.time()
        
        user_data = {
            "login": "benchuser",
            "senha": "BenchPass123@",
            "email": "bench@example.com",
            "tag": "cliente"
        }
        
        create_start = time.time()
        create_response = client.post("/cadastro", json=user_data)
        create_time = time.time() - create_start
        
        if create_response.status_code != status.HTTP_200_OK:
            pytest.skip("Rate limiting ativo, pulando benchmark CRUD")
        
        user_id = create_response.json()["id"]
        
        login_start = time.time()
        login_response = client.post("/login", json={
            "email_ou_login": user_data["email"],
            "senha": user_data["senha"]
        })
        login_time = time.time() - login_start
        
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        read_start = time.time()
        read_response = client.get(f"/usuarios/{user_id}", headers=headers)
        read_time = time.time() - read_start
        
        assert read_response.status_code == status.HTTP_200_OK
        
        update_start = time.time()
        update_response = client.put(f"/usuarios/{user_id}", 
                                   json={"tag": "tester"}, 
                                   headers=headers)
        update_time = time.time() - update_start
        
        assert update_response.status_code == status.HTTP_200_OK
        
        total_time = time.time() - total_start
        
        print(f"\n🔄 BENCHMARK CRUD COMPLETO:")
        print(f"   - CREATE: {create_time:.3f}s")
        print(f"   - LOGIN: {login_time:.3f}s")  
        print(f"   - READ: {read_time:.3f}s")
        print(f"   - UPDATE: {update_time:.3f}s")
        print(f"   - TOTAL: {total_time:.3f}s")
        
        assert create_time < 3.0, f"CREATE muito lento: {create_time:.3f}s"
        assert login_time < 2.0, f"LOGIN muito lento: {login_time:.3f}s"
        assert read_time < 1.0, f"READ muito lento: {read_time:.3f}s"
        assert update_time < 2.0, f"UPDATE muito lento: {update_time:.3f}s"
        assert total_time < 8.0, f"CRUD total muito lento: {total_time:.3f}s"

class TestPerformanceRegression:
    """Testes para detectar regressão de performance"""
    
    def test_performance_baseline_health(self, client):
        """Estabelece baseline de performance para health check"""
        times = []
        
        for _ in range(5):
            start = time.time()
            response = client.get("/health")
            end = time.time()
            
            assert response.status_code == status.HTTP_200_OK
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\n📈 BASELINE HEALTH CHECK:")
        print(f"   - Tempo médio: {avg_time:.3f}s")
        print(f"   - Tempo mínimo: {min_time:.3f}s")
        print(f"   - Tempo máximo: {max_time:.3f}s")
        
        assert avg_time < 0.5, f"Baseline health check degradado: {avg_time:.3f}s"
        assert max_time < 1.0, f"Pior caso health check muito lento: {max_time:.3f}s"

    def test_performance_baseline_jwt(self, client, auth_headers):
        """Estabelece baseline para operações JWT"""
        times = []
        
        for _ in range(5):
            start = time.time()
            response = client.get("/me", headers=auth_headers)
            end = time.time()
            
            assert response.status_code == status.HTTP_200_OK
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n🔐 BASELINE JWT VERIFICATION:")
        print(f"   - Tempo médio: {avg_time:.3f}s")
        print(f"   - Tempo máximo: {max_time:.3f}s")
        
        assert avg_time < 1.0, f"Baseline JWT degradado: {avg_time:.3f}s"
        assert max_time < 2.0, f"Pior caso JWT muito lento: {max_time:.3f}s"

class TestPerformanceStress:
    """Testes de stress básicos"""
    
    def test_stress_health_endpoint(self, client):
        """Teste de stress do endpoint de health"""
        def make_request():
            try:
                return client.get("/health").status_code
            except:
                return 500
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        sucessos = sum(1 for status in results if status == 200)
        taxa_sucesso = sucessos / len(results)
        
        print(f"\n💪 STRESS TEST HEALTH:")
        print(f"   - Total requests: {len(results)}")
        print(f"   - Sucessos: {sucessos}")
        print(f"   - Taxa de sucesso: {taxa_sucesso:.2%}")
        print(f"   - Tempo total: {total_time:.3f}s")
        
        assert taxa_sucesso >= 0.8, f"Taxa de sucesso muito baixa: {taxa_sucesso:.2%}"
        
        assert total_time < 10.0, f"Stress test muito lento: {total_time:.3f}s"

    def test_stress_mixed_operations(self, client, created_user, sample_user_data):
        """Teste de stress com operações mistas"""
        def operacao_health():
            return client.get("/health").status_code
            
        def operacao_login():
            try:
                response = client.post("/login", json={
                    "email_ou_login": sample_user_data["email"],
                    "senha": sample_user_data["senha"]
                })
                return response.status_code
            except:
                return 500
        
        def operacao_rate_limit():
            return client.get("/rate-limit-status").status_code
        
        operations = [
            operacao_health, operacao_health, operacao_health,
            operacao_rate_limit, operacao_rate_limit,
            operacao_login
        ]
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(op) for op in operations]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        sucessos = sum(1 for status in results if status in [200, 401, 429])
        taxa_sucesso = sucessos / len(results)
        
        print(f"\n🎯 STRESS TEST MISTO:")
        print(f"   - Operações: {len(results)}")
        print(f"   - Sucessos: {sucessos}")
        print(f"   - Taxa de sucesso: {taxa_sucesso:.2%}")
        print(f"   - Tempo total: {total_time:.3f}s")
        
        assert taxa_sucesso >= 0.7, f"Taxa de sucesso muito baixa: {taxa_sucesso:.2%}"
        assert total_time < 15.0, f"Operações mistas muito lentas: {total_time:.3f}s".time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0, f"Health check muito lento: {response_time:.3f}s"

    def test_tempo_resposta_root(self, client):
        """Testa tempo de resposta do endpoint raiz"""
        start_time = time.time()
        
        response = client.get("/")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0, f"Root endpoint muito lento: {response_time:.3f}s"

    def test_tempo_resposta_cadastro(self, client):
        """Testa tempo de resposta do cadastro"""
        user_data = {
            "login": "perfuser",
            "senha": "PerfPass123@",
            "email": "perf@example.com",
            "tag": "cliente"
        }
        
        start_time = time.time()
        
        response = client.post("/cadastro", json=user_data)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 3.0, f"Cadastro muito lento: {response_time:.3f}s"

    def test_tempo_resposta_login(self, client, created_user, sample_user_data):
        """Testa tempo de resposta do login"""
        login_data = {
            "email_ou_login": sample_user_data["email"],
            "senha": sample_user_data["senha"]
        }
        
        start_time = time.time()
        
        response = client.post("/login", json=login_data)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 2.0, f"Login muito lento: {response_time:.3f}s"

class TestPerformanceLoad:
    """Testes de carga básicos"""
    
    def test_multiplas_requisicoes_health(self, client):
        """Testa múltiplas requisições simultâneas ao health check"""
        def fazer_requisicao():
            return client.get("/health")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fazer_requisicao) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        for response in results:
            assert response.status_code == status.HTTP_200_OK
        
        assert total_time < 5.0, f"10 requisições muito lentas: {total_time:.3f}s"
        
        avg_time = total_time / len(results)
        assert avg_time < 1.0, f"Tempo médio muito alto: {avg_time:.3f}s"

    def test_multiplos_cadastros_sequenciais(self, client):
        """Testa múltiplos cadastros sequenciais"""
        cadastros_realizados = 0
        tempos_resposta = []
        
        for i in range(5): 
            user_data = {
                "login": f"loaduser{i}",
                "senha": f"LoadPass{i}@",
                "email": f"load{i}@example.com",
                "tag": "cliente"
            }
            
            start_time = time.time()
            
            try:
                response = client.post("/cadastro", json=user_data)
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == status.HTTP_200_OK:
                    cadastros_realizados += 1
                    tempos_resposta.append(response_time)
                elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                    time.sleep(1)
                    continue
                
            except Exception as e:
                print(f"Erro no cadastro {i}: {e}")
                continue
        
        assert cadastros_realizados > 0, "Nenhum cadastro foi realizado"
        
        if tempos_resposta:
            tempo_medio = sum(tempos_resposta) / len(tempos_resposta)
            assert tempo_medio < 3.0, f"Tempo médio de cadastro muito alto: {tempo_medio:.3f}s"

    def test_multiplos_logins_usuario_existente(self, client, created_user, sample_user_data):
        """Testa múltiplos logins do mesmo usuário"""
        login_data = {
            "email_ou_login": sample_user_data["email"],
            "senha": sample_user_data["senha"]
        }
        
        logins_realizados = 0
        tempos_resposta = []
        
        for i in range(3):
            start_time = time.time()
            
            try:
                response = client.post("/login", json=login_data)
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == status.HTTP_200_OK:
                    logins_realizados += 1
                    tempos_resposta.append(response_time)
                elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                    break
                    
            except Exception as e:
                print(f"Erro no login {i}: {e}")
                continue
        
        assert logins_realizados > 0, "Nenhum login foi realizado"
        
        if tempos_resposta:
            tempo_medio = sum(tempos_resposta) / len(tempos_resposta)
            assert tempo_medio < 2.0, f"Tempo médio de login muito alto: {tempo_medio:.3f}s"

class TestPerformanceDatabase:
    """Testes de performance do banco de dados"""
    
    def test_listagem_usuarios_com_dados(self, client, admin_auth_headers, db_session):
        """Testa performance da listagem com vários usuários"""
        from app.models.user import Usuario
        from app.utils.jwt_auth import hash_password
        from datetime import datetime
        
        usuarios_teste = []
        for i in range(10):
            usuario = Usuario(
                login=f"perfuser{i}",
                senha=hash_password("TestPass123@"),
                email=f"perfuser{i}@example.com",
                tag="cliente",
                plan="trial",
                credencial=f"cred{i}",
                created_at=datetime.utcnow()
            )
            db_session.add(usuario)
            usuarios_teste.append(usuario)
        
        db_session.commit()
        
        start_time = time.time()
        
        response = client.get("/usuarios", headers=admin_auth_headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 2.0, f"Listagem muito lenta: {response_time:.3f}s"
        
        data = response.json()
        assert len(data) >= 10, "Nem todos os usuários foram retornados"

    def test_busca_usuario_por_id_performance(self, client, admin_auth_headers, created_user):
        """Testa performance da busca por ID"""
        start_time = time.time()
        
        response = client.get(f"/usuarios/{created_user.id}", headers=admin_auth_headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0, f"Busca por ID muito lenta: {response_time:.3f}s"

    def test_busca_usuario_inexistente_performance(self, client, admin_auth_headers):
        """Testa performance da busca por usuário inexistente"""
        start_time = time.time()
        
        response = client.get("/usuarios/99999", headers=admin_auth_headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_time < 1.0, f"Busca de inexistente muito lenta: {response_time:.3f}s"

class TestPerformanceJWT:
    """Testes de performance do JWT"""
    
    def test_verificacao_token_performance(self, client, auth_headers):
        """Testa performance da verificação de token"""
        start_time = time.time()
        
        response = client.get("/me", headers=auth_headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0, f"Verificação de token muito lenta: {response_time:.3f}s"

    def test_multiplas_verificacoes_token(self, client, auth_headers):
        """Testa múltiplas verificações do mesmo token"""
        def verificar_token():
            return client.get("/me", headers=auth_headers)
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(verificar_token) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        for response in results:
            assert response.status_code == status.HTTP_200_OK
        
        assert total_time < 3.0, f"Verificações múltiplas muito lentas: {total_time:.3f}s"

class TestPerformanceMemory:
    """Testes básicos de uso de memória"""
    
    def test_cadastro_nao_vaza_memoria(self, client):
        """Testa se cadastros sucessivos não causam vazamento de memória"""
        import gc
        import sys
        
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        for i in range(5):
            user_data = {
                "login": f"memuser{i}",
                "senha": f"MemPass{i}@",
                "email": f"mem{i}@example.com",
                "tag": "cliente"
            }
            
            try:
                response = client.post("/cadastro", json=user_data)
                if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                    time.sleep(1)
                    continue
            except Exception:
                continue
        
        gc.collect()
        final_objects = len(gc.get_objects())
        
        object_increase = final_objects - initial_objects
        
        assert object_increase < 1000, f"Possível vazamento de memória: {object_increase} novos objetos"

class TestPerformanceRateLimit:
    """Testes de performance do rate limiting"""
    
    def test_rate_limit_nao_afeta_performance_normal(self, client):
        """Testa se rate limiting não afeta performance de uso normal"""
        start_time = time.time()
        
        response = client.get("/health")
        
        end_time = time