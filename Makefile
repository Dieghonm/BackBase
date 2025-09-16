# Makefile para BackBase API - Comandos de Teste

.PHONY: help install test test-fast test-auth test-crud test-security test-performance test-coverage test-html clean setup-test

# Configurações
PYTHON = python3
PIP = pip3
PYTEST = python -m pytest

# Cores para output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Mostra esta ajuda
	@echo "$(BLUE)BackBase API - Comandos de Teste$(NC)"
	@echo "================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala dependências de teste
	@echo "$(BLUE)📦 Instalando dependências de teste...$(NC)"
	$(PIP) install -r requirements-test.txt
	@echo "$(GREEN)✅ Dependências instaladas!$(NC)"

setup-test: ## Configuração inicial para testes
	@echo "$(BLUE)🔧 Configurando ambiente de teste...$(NC)"
	mkdir -p tests reports htmlcov logs
	@echo "$(GREEN)✅ Ambiente configurado!$(NC)"

test: ## Executa todos os testes
	@echo "$(BLUE)🧪 Executando todos os testes...$(NC)"
	$(PYTEST) tests/ -v

test-fast: ## Executa testes rápidos (sem testes lentos)
	@echo "$(BLUE)⚡ Executando testes rápidos...$(NC)"
	$(PYTEST) tests/ -v -m "not slow"

test-auth: ## Executa apenas testes de autenticação
	@echo "$(BLUE)🔐 Executando testes de autenticação...$(NC)"
	$(PYTEST) tests/test_auth.py -v

test-crud: ## Executa apenas testes de CRUD
	@echo "$(BLUE)📝 Executando testes de CRUD...$(NC)"
	$(PYTEST) tests/test_users.py -v

test-security: ## Executa apenas testes de segurança
	@echo "$(BLUE)🛡️  Executando testes de segurança...$(NC)"
	$(PYTEST) tests/test_security.py -v

test-endpoints: ## Executa testes de endpoints
	@echo "$(BLUE)🌐 Executando testes de endpoints...$(NC)"
	$(PYTEST) tests/test_endpoints.py -v

test-performance: ## Executa testes de performance
	@echo "$(BLUE)📊 Executando testes de performance...$(NC)"
	$(PYTEST) tests/test_performance.py -v

test-unit: ## Executa apenas testes unitários
	@echo "$(BLUE)🔬 Executando testes unitários...$(NC)"
	$(PYTEST) tests/ -v -m "unit"

test-integration: ## Executa apenas testes de integração
	@echo "$(BLUE)🔗 Executando testes de integração...$(NC)"
	$(PYTEST) tests/ -v -m "integration"

test-coverage: ## Executa testes com cobertura de código
	@echo "$(BLUE)📊 Executando testes com cobertura...$(NC)"
	$(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)📋 Relatório de cobertura: htmlcov/index.html$(NC)"

test-html: ## Executa testes e gera relatório HTML
	@echo "$(BLUE)📋 Executando testes com relatório HTML...$(NC)"
	$(PYTEST) tests/ --html=reports/report.html --self-contained-html
	@echo "$(GREEN)📄 Relatório HTML: reports/report.html$(NC)"

test-parallel: ## Executa testes em paralelo
	@echo "$(BLUE)🔀 Executando testes em paralelo...$(NC)"
	$(PYTEST) tests/ -n auto -v

test-stress: ## Executa testes de stress
	@echo "$(YELLOW)💪 Executando testes de stress...$(NC)"
	$(PYTEST) tests/test_performance.py -v -k "stress"

test-debug: ## Executa testes com debug detalhado
	@echo "$(BLUE)🔍 Executando testes com debug...$(NC)"
	$(PYTEST) tests/ -v -s --tb=long

test-specific: ## Executa teste específico (use: make test-specific TEST=nome_do_teste)
	@echo "$(BLUE)🎯 Executando teste específico: $(TEST)$(NC)"
	$(PYTEST) tests/ -v -k "$(TEST)"

test-failed: ## Re-executa apenas testes que falharam
	@echo "$(BLUE)🔄 Re-executando testes que falharam...$(NC)"
	$(PYTEST) tests/ --lf -v

test-all-reports: ## Executa todos os testes com todos os relatórios
	@echo "$(BLUE)📊 Executando suite completa de testes...$(NC)"
	$(PYTEST) tests/ -v \
		--cov=app \
		--cov-report=html:htmlcov \
		--cov-report=term-missing \
		--html=reports/report.html \
		--self-contained-html
	@echo "$(GREEN)✅ Testes completos executados!$(NC)"
	@echo "$(GREEN)📊 Cobertura: htmlcov/index.html$(NC)"
	@echo "$(GREEN)📋 Relatório: reports/report.html$(NC)"

# Comandos de limpeza
clean: ## Remove arquivos temporários e relatórios
	@echo "$(YELLOW)🧹 Limpando arquivos temporários...$(NC)"
	rm -rf __pycache__ .pytest_cache .coverage htmlcov reports
	rm -rf tests/__pycache__ app/__pycache__
	rm -f test.db banco.db
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

clean-db: ## Remove bancos de dados de teste
	@echo "$(YELLOW)🗄️  Removendo bancos de teste...$(NC)"
	rm -f test.db banco.db *.db
	@echo "$(GREEN)✅ Bancos removidos!$(NC)"

# Comandos de verificação de código
lint: ## Executa verificação de estilo de código
	@echo "$(BLUE)📏 Verificando estilo de código...$(NC)"
	flake8 app/ tests/
	@echo "$(GREEN)✅ Verificação concluída!$(NC)"

format: ## Formata código com black
	@echo "$(BLUE)✨ Formatando código...$(NC)"
	black app/ tests/
	isort app/ tests/
	@echo "$(GREEN)✅ Código formatado!$(NC)"

# Comandos de CI/CD
ci-test: ## Executa testes para CI/CD (com cobertura e relatórios)
	@echo "$(BLUE)🚀 Executando testes para CI/CD...$(NC)"
	$(PYTEST) tests/ \
		--cov=app \
		--cov-report=xml:reports/coverage.xml \
		--cov-report=html:htmlcov \
		--cov-report=term-missing \
		--html=reports/report.html \
		--self-contained-html \
		--junit-xml=reports/junit.xml \
		-v
	@echo "$(GREEN)✅ Testes de CI/CD concluídos!$(NC)"

# Comandos de desenvolvimento
dev-test: ## Executa testes em modo desenvolvimento (com watch)
	@echo "$(BLUE)👨‍💻 Executando testes em modo desenvolvimento...$(NC)"
	$(PYTEST) tests/ -v --tb=short -x

quick-test: ## Execução super rápida para desenvolvimento
	@echo "$(BLUE)⚡ Execução super rápida...$(NC)"
	$(PYTEST) tests/test_auth.py::TestAuth::test_hash_password -v

# Comandos informativos
show-coverage: ## Mostra relatório de cobertura no terminal
	@echo "$(BLUE)📊 Relatório de cobertura:$(NC)"
	@if [ -f .coverage ]; then \
		coverage report; \
	else \
		echo "$(YELLOW)⚠️  Execute 'make test-coverage' primeiro$(NC)"; \
	fi

show-reports: ## Lista relatórios disponíveis
	@echo "$(BLUE)📋 Relatórios disponíveis:$(NC)"
	@ls -la htmlcov/ reports/ 2>/dev/null || echo "$(YELLOW)⚠️  Nenhum relatório encontrado$(NC)"

# Benchmarks
benchmark: ## Executa benchmarks de performance
	@echo "$(BLUE)🏃 Executando benchmarks...$(NC)"
	$(PYTEST) tests/test_performance.py::TestPerformanceBenchmarks -v

# Comandos utilitários
check-env: ## Verifica se o ambiente está configurado
	@echo "$(BLUE)🔍 Verificando ambiente...$(NC)"
	@$(PYTHON) --version
	@$(PIP) --version
	@echo "$(GREEN)✅ Ambiente OK!$(NC)"

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(BLUE)📦 Instalando dependências de desenvolvimento...$(NC)"
	$(PIP) install -r requirements-test.txt
	$(PIP) install pre-commit
	pre-commit install
	@echo "$(GREEN)✅ Ambiente de desenvolvimento configurado!$(NC)"

# Comandos de pipeline completo
full-check: clean install test-all-reports lint ## Pipeline completo de verificação
	@echo "$(GREEN)🎉 Verificação completa concluída com sucesso!$(NC)"

# Comandos de debug
debug-failed: ## Debug detalhado dos testes que falharam
	@echo "$(BLUE)🔍 Debug detalhado dos testes que falharam...$(NC)"
	$(PYTEST) tests/ --lf -v -s --tb=long --pdb

# Aliases úteis
t: test ## Alias para 'test'
tf: test-fast ## Alias para 'test-fast'
tc: test-coverage ## Alias para 'test-coverage'
th: test-html ## Alias para 'test-html'