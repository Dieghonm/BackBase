# 🧪 Testes Automatizados - BackBase API

Documentação completa da suite de testes automatizados para a API BackBase.

## 📁 Estrutura dos Testes

```
tests/
├── conftest.py              # Configurações e fixtures compartilhadas
├── test_auth.py             # Testes de autenticação e JWT
├── test_users.py            # Testes de CRUD de usuários
├── test_security.py         # Testes de segurança
├── test_endpoints.py        # Testes de endpoints HTTP
├── test_performance.py      # Testes de performance e carga
└── README.md               # Esta documentação
```

## 🚀 Executando os Testes

### Opção 1: Usando Makefile (Recomendado)

```bash
# Ver todas as opções
make help

# Executar todos os testes
make test

# Testes rápidos (sem testes lentos)
make test-fast

# Testes específicos
make test-auth      # Só autenticação
make test-crud      # Só CRUD
make test-security  # Só segurança

# Testes com relatórios
make test-coverage  # Com cobertura de código
make test-html      # Com relatório HTML
```

### Opção 2: Usando Script Python

```bash
# Executar script de testes
python run_tests.py --type all --coverage --html

# Opções disponíveis
python run_tests.py --help
```

### Opção 3: Usando pytest Diretamente

```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_auth.py -v
pytest tests/test_users.py::TestUserService::test_criar_usuario_success -v

# Com cobertura
pytest tests/ --cov=app --cov-report=html
```

## 📊 Tipos de Teste

### 🔐 Testes de Autenticação (`test_auth.py`)

- **Hash de senhas**: Bcrypt, verificação, salt único
- **JWT**: Criação, validação, expiração (1 mês)
- **Login**: Credenciais válidas/inválidas, rate limiting
- **Endpoints protegidos**: Middleware de autenticação
- **Rate limiting**: Proteção contra força bruta

**Principais classes:**
- `TestAuth` - Funcionalidades básicas de auth
- `TestAuthEndpoints` - Endpoints de login
- `TestRateLimiting` - Limitação de requisições
- `TestJWTIntegration` - Integração JWT com endpoints

### 👤 Testes de Usuários (`test_users.py`)

- **CRUD completo**: Create, Read, Update, Delete
- **Validações**: Email único, login único, formatos
- **Serviços**: Todas as funções do `user_service.py`
- **Endpoints**: Todos os endpoints de usuário
- **Permissões**: Admin vs usuário normal

**Principais classes:**
- `TestUserService` - Lógica de negócio
- `TestUserEndpoints` - Endpoints HTTP
- `TestUserValidation` - Validações de entrada
- `TestUserEdgeCases` - Casos extremos

### 🛡️ Testes de Segurança (`test_security.py`)

- **Senhas**: Hash seguro, verificação, força
- **JWT**: Tokens inválidos, manipulação, expiração
- **SQL Injection**: Tentativas de injeção
- **XSS**: Prevenção de scripts maliciosos
- **Autorização**: Escalação de privilégios

**Principais classes:**
- `TestPasswordSecurity` - Segurança de senhas
- `TestJWTSecurity` - Segurança JWT
- `TestAuthenticationSecurity` - Auth geral
- `TestAuthorizationSecurity` - Permissões/roles

### 🌐 Testes de Endpoints (`test_endpoints.py`)

- **Health checks**: Status da API
- **Formato de respostas**: Estrutura JSON
- **Códigos HTTP**: Status corretos
- **Headers**: CORS, Authorization
- **Tratamento de erros**: Respostas adequadas

**Principais classes:**
- `TestHealthEndpoints` - Health e status
- `TestCadastroEndpoint` - Endpoint de cadastro
- `TestLoginEndpoint` - Endpoint de login
- `TestErrorHandling` - Tratamento de erros

### ⚡ Testes de Performance (`test_performance.py`)

- **Tempo de resposta**: Limites aceitáveis
- **Carga**: Múltiplas requisições simultâneas
- **Benchmarks**: Métricas de performance
- **Stress**: Testes de stress básicos
- **Regressão**: Detecção de degradação

**Principais classes:**
- `TestPerformanceBasic` - Tempos básicos
- `TestPerformanceLoad` - Testes de carga
- `TestPerformanceBenchmarks` - Benchmarks
- `TestPerformanceStress` - Testes de stress

## 🔧 Fixtures Principais (`conftest.py`)

### Banco de Dados
- `db_session` - Sessão limpa para cada teste
- `db_engine` - Engine do banco de teste

### Usuários de Teste
- `sample_user_data` - Dados de usuário normal
- `admin_user_data` - Dados de usuário admin
- `created_user` - Usuário já criado no banco
- `created_admin_user` - Admin já criado no banco

### Autenticação
- `user_token` - Token JWT para usuário normal
- `admin_token` - Token JWT para admin
- `auth_headers` - Headers de autenticação
- `admin_auth_headers` - Headers de admin

### Cliente de Teste
- `client` - TestClient configurado do FastAPI

## 📈 Relatórios e Cobertura

### Cobertura de Código
```bash
# Gerar relatório de cobertura
make test-coverage

# Ver no navegador
open htmlcov/index.html
```

### Relatório HTML
```bash
# Gerar relatório HTML dos testes
make test-html

# Ver no navegador
open reports/report.html
```

### Benchmarks de Performance
```bash
# Executar benchmarks
make benchmark

# Ver métricas no terminal
```

## 🏷️ Markers Personalizados

Use markers para categorizar testes:

```python
@pytest.mark.slow
def test_operacao_lenta():
    pass

@pytest.mark.integration  
def test_integracao_completa():
    pass

@pytest.mark.security
def test_seguranca_critica():
    pass
```

Executar por markers:
```bash
# Só testes rápidos
pytest tests/ -m "not slow"

# Só testes de integração
pytest tests/ -m "integration"

# Só testes de segurança
pytest tests/ -m "security"
```

## 📋 Checklist de Testes

Antes de fazer commit, certifique-se que:

- [ ] ✅ Todos os testes passam (`make test`)
- [ ] 📊 Cobertura acima de 80% (`make test-coverage`)
- [ ] ⚡ Performance dentro dos limites (`make test-performance`)
- [ ] 🛡️ Testes de segurança passam (`make test-security`)
- [ ] 🧹 Código formatado (`make format`)
- [ ] 📏 Linting OK (`make lint`)

## 🐛 Debug de Testes

### Executar teste específico
```bash
# Por nome da função
pytest tests/ -k "test_login_success" -v

# Por classe
pytest tests/test_auth.py::TestAuth -v

# Por arquivo específico
pytest tests/test_users.py -v
```

### Debug com breakpoints
```bash
# Parar no primeiro erro
pytest tests/ -x -s

# Debug interativo
pytest tests/ --pdb

# Apenas testes que falharam
pytest tests/ --lf -v
```

### Testes verbosos
```bash
# Output detalhado
pytest tests/ -v -s --tb=long

# Com prints dos testes
pytest tests/ -s
```

## 🚀 Integração Contínua

Para CI/CD, use:
```bash
make ci-test
```

Este comando:
- Executa todos os testes
- Gera relatório de cobertura (XML + HTML)  
- Gera relatório JUnit para CI
- Gera relatório HTML
- Falha se cobertura < 80%

## 🔄 Testes em Desenvolvimento

Durante desenvolvimento:
```bash
# Modo watch (re-executa quando arquivos mudam)
make dev-test

# Super rápido para verificação
make quick-test

# Só testes que falharam
make test-failed
```

## 📚 Adicionando Novos Testes

### 1. Estrutura Básica
```python
import pytest
from fastapi import status

class TestNoveFuncionalidade:
    """Testes para nova funcionalidade"""
    
    def test_caso_basico(self, client):
        """Testa caso básico"""
        response = client.get("/novo-endpoint")
        assert response.status_code == status.HTTP_200_OK
```

### 2. Use Fixtures Existentes
```python
def test_com_usuario(self, client, created_user, auth_headers):
    """Usa fixtures já disponíveis"""
    response = client.get("/endpoint", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
```

### 3. Adicione Markers
```python
@pytest.mark.integration
@pytest.mark.slow
def test_integracao_complexa(self):
    """Teste de integração que demora"""
    pass
```

### 4. Documente o Teste
```python
def test_funcionalidade_especifica(self):
    """
    Testa funcionalidade X quando condição Y
    
    Cenário:
    1. Usuário faz login
    2. Acessa endpoint protegido
    3. Deve receber dados corretos
    """
    pass
```

## ⚠️ Limitações Conhecidas

1. **Rate Limiting**: Alguns testes podem falhar se executados muito rapidamente
2. **Banco em Memória**: Performance pode variar do banco real
3. **Concorrência**: Testes paralelos podem ter conflitos ocasionais
4. **Fixtures**: Algumas fixtures criam dados que persistem durante o teste

## 💡 Dicas e Boas Práticas

### ✅ Faça
- Use fixtures para setup comum
- Teste casos extremos (edge cases)
- Mantenha testes independentes
- Use nomes descritivos para testes
- Adicione markers apropriados

### ❌ Evite  
- Testes que dependem de outros testes
- Hard-code de valores que podem mudar
- Testes muito longos ou complexos
- Skip testes sem boa razão
- Testes sem assertions

## 🆘 Solução de Problemas

### Problema: Banco de dados já existe
```bash
make clean-db
```

### Problema: Testes lentos
```bash
make test-fast
```

### Problema: Rate limiting atrapalhando
```bash
# Aguardar entre execuções ou usar testes específicos
pytest tests/test_auth.py::TestAuth::test_hash_password
```

### Problema: Import errors
```bash
# Verificar se está na raiz do projeto
cd /caminho/para/backbase
export PYTHONPATH=$PWD:$PYTHONPATH
```

## 📞 Suporte

Para dúvidas sobre os testes:
1. Verifique esta documentação
2. Execute `make help` para ver comandos
3. Use `pytest --help` para opções do pytest
4. Verifique os comentários nos arquivos de teste