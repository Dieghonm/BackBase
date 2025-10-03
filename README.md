# 🚀 BackBase API

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.23-red?style=for-the-badge&logo=sqlalchemy)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**API RESTful de alto desempenho para gerenciamento de usuários com autenticação JWT, rate limiting e arquitetura escalável.**

[📖 Documentação](#-documentação) • [🚀 Quick Start](#-quick-start) • [🔧 Deploy](#-deploy-no-render) • [📚 API Reference](#-endpoints-da-api)

</div>

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Features](#-features)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Quick Start](#-quick-start)
- [Configuração](#-configuração)
- [Endpoints da API](#-endpoints-da-api)
- [Autenticação](#-autenticação)
- [Deploy no Render](#-deploy-no-render)
- [Testes](#-testes)
- [Segurança](#-segurança)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

BackBase API é uma solução completa e production-ready para gerenciamento de usuários, construída com FastAPI e seguindo as melhores práticas de desenvolvimento de APIs RESTful.

### Diferencial

- ✅ **Autenticação JWT** com tokens de longa duração (30 dias)
- ✅ **Rate Limiting** integrado para proteção contra ataques
- ✅ **Arquitetura limpa** com separação de responsabilidades
- ✅ **Validações robustas** usando Pydantic
- ✅ **Documentação automática** com Swagger UI e ReDoc
- ✅ **Pronto para produção** com configuração para Render

---

## ✨ Features

### 🔐 Autenticação e Segurança
- [x] Autenticação JWT (Bearer Token)
- [x] Tokens com validade de 30 dias
- [x] Hash de senhas com bcrypt
- [x] Rate limiting por endpoint
- [x] CORS configurável por ambiente
- [x] Validação de força de senha

### 👥 Gerenciamento de Usuários
- [x] Cadastro com validação completa
- [x] Login com email/username
- [x] Renovação de token automática
- [x] Sistema de roles (admin, tester, cliente)
- [x] Planos de usuário (trial, mensal, trimestral, semestral, anual)
- [x] Listagem e busca de usuários

### 🛡️ Proteção e Performance
- [x] Rate limiting: 10 req/min para login
- [x] Rate limiting: 5 req/min para cadastro
- [x] Validação de dados em múltiplas camadas
- [x] Tratamento de erros detalhado
- [x] Health check endpoint

---

## 🛠️ Tecnologias

| Categoria | Tecnologia |
|-----------|-----------|
| **Framework** | FastAPI 0.104.1 |
| **Servidor** | Uvicorn 0.24.0 |
| **Banco de Dados** | SQLAlchemy 2.0.23 + SQLite/PostgreSQL |
| **Validação** | Pydantic 2.11.9 |
| **Autenticação** | JWT (python-jose) |
| **Segurança** | bcrypt + passlib |
| **Rate Limiting** | SlowAPI |
| **Configuração** | python-dotenv |

---

## 🏗️ Arquitetura

```
app/
├── core/                    # Configurações centrais
│   ├── config.py           # Settings e variáveis de ambiente
│   └── constants.py        # Constantes da aplicação
├── database/               # Camada de dados
│   ├── connection.py       # Engine e Base do SQLAlchemy
│   ├── session.py          # SessionLocal e get_db
│   ├── migrations.py       # Criação de tabelas
│   └── seeds.py            # Dados iniciais
├── models/                 # Modelos SQLAlchemy
│   └── user.py            # Modelo de usuário
├── schemas/                # Schemas Pydantic
│   └── schemas.py         # Validações de entrada/saída
├── services/               # Lógica de negócio
│   ├── user_service.py    # CRUD de usuários
│   └── auth_service.py    # Autenticação
├── utils/                  # Utilitários
│   ├── jwt_auth.py        # Funções JWT
│   └── security.py        # Segurança e validações
└── main.py                # Aplicação principal
```

### Princípios Arquiteturais

- **Separation of Concerns**: Cada módulo tem uma responsabilidade única
- **Dependency Injection**: Uso de FastAPI's Depends
- **Schema Validation**: Pydantic para validação em tempo de execução
- **Service Layer Pattern**: Lógica de negócio isolada dos endpoints

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/BackBase.git
cd BackBase

# 2. Crie um ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instale as dependências
pip install --upgrade pip
pip install -r requirements.txt

# 5. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 6. Execute a aplicação
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Acesso Rápido

Após iniciar o servidor:

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true

# Banco de dados
DATABASE_URL=sqlite:///./banco.db

# Segurança (GERAR NOVAS CHAVES!)
SECRET_KEY=sua-chave-secreta-super-segura
JWT_SECRET_KEY=sua-chave-jwt-super-segura
ALGORITHM=HS256

# JWT - Token válido por 30 dias
ACCESS_TOKEN_EXPIRE_MINUTES=43200
JWT_EXPIRE_MINUTES=43200

# Rate Limiting
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_CADASTRO=5/minute

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### Gerar Chaves Secretas

```bash
# Gerar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Gerar JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📚 Endpoints da API

### 🔓 Públicos (Sem autenticação)

#### `GET /`
Informações da API

**Resposta:**
```json
{
  "message": "BackBase API está funcionando!",
  "status": "online",
  "version": "1.0.0",
  "features": ["JWT Authentication", "User Management", "Rate Limiting"]
}
```

#### `GET /health`
Health check

**Resposta:**
```json
{
  "status": "healthy",
  "message": "API está funcionando corretamente"
}
```

#### `POST /cadastro`
Cadastra um novo usuário

**Rate Limit**: 5 requisições/minuto

**Body:**
```json
{
  "login": "usuario123",
  "senha": "Senha@123",
  "email": "usuario@example.com",
  "tag": "cliente",
  "plan": "trial"
}
```

**Validações:**
- **login**: 3-50 caracteres, apenas letras, números e underscore
- **senha**: mínimo 8 caracteres
- **email**: formato válido
- **tag**: `admin`, `tester` ou `cliente`
- **plan**: `trial`, `mensal`, `trimestral`, `semestral`, `anual`

**Resposta de Sucesso (201):**
```json
{
  "sucesso": true,
  "message": "Usuário criado com sucesso",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "timing": 15,
  "user": {
    "login": "usuario123"
  },
  "created_at": "2025-10-03T10:30:00Z"
}
```

#### `POST /login`
Autentica um usuário

**Rate Limit**: 10 requisições/minuto

**Método 1: Credenciais**
```json
{
  "email_ou_login": "usuario@example.com",
  "senha": "Senha@123"
}
```

**Método 2: Renovação de Token**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_duration": "1_month",
  "timing": 15,
  "user": {
    "login": "usuario123"
  }
}
```

### 🔒 Protegidos (Requer autenticação)

**Header necessário:**
```
Authorization: Bearer seu-token-jwt
```

#### `GET /me`
Retorna dados do usuário autenticado

**Resposta:**
```json
{
  "id": 1,
  "login": "usuario123",
  "email": "usuario@example.com",
  "tag": "cliente",
  "plan": "trial",
  "created_at": "2025-10-03T10:30:00Z"
}
```

#### `GET /usuarios`
Lista todos os usuários (admin/tester apenas)

**Resposta:**
```json
[
  {
    "id": 1,
    "login": "usuario123",
    "email": "usuario@example.com",
    "tag": "cliente",
    "plan": "trial",
    "created_at": "2025-10-03T10:30:00Z"
  }
]
```

---

## 🔐 Autenticação

### Como usar JWT

1. **Cadastre-se ou faça login** para obter um token
2. **Inclua o token** em requisições protegidas:

```bash
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer seu-token-aqui"
```

3. **Renove o token** quando necessário (antes de expirar):

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"token": "seu-token-atual"}'
```

### Duração do Token

- **Validade**: 30 dias (43200 minutos)
- **Renovação**: Automática via endpoint `/login`
- **Segurança**: Hash SHA256 com chave secreta

---

## 🌐 Deploy no Render

### Passo 1: Preparar o Projeto

1. **Crie o arquivo `render.yaml`** na raiz do projeto (já fornecido)

2. **Atualize o `.gitignore`** para não commitar arquivos sensíveis:
```gitignore
.env
.env.local
.env.production
*.db
__pycache__/
```

3. **Commit e push** para o GitHub:
```bash
git add .
git commit -m "Preparando para deploy no Render"
git push origin main
```

### Passo 2: Deploy no Render

1. **Acesse** [https://render.com](https://render.com) e faça login

2. **Clique em "New +"** → **"Blueprint"**

3. **Conecte seu repositório** GitHub

4. **Render detectará automaticamente** o arquivo `render.yaml`

5. **Configure as variáveis de ambiente** (crítico!):

   - `SECRET_KEY`: Gere uma nova chave
   - `JWT_SECRET_KEY`: Gere uma nova chave
   - `CORS_ORIGINS`: Adicione seus domínios frontend

6. **Clique em "Apply"** e aguarde o deploy

### Passo 3: Configuração Pós-Deploy

#### Variáveis de Ambiente Obrigatórias

No Dashboard do Render, configure:

```bash
# Gerar novas chaves secretas
SECRET_KEY=nova-chave-gerada
JWT_SECRET_KEY=nova-chave-jwt-gerada

# CORS - Adicionar seus domínios reais
CORS_ORIGINS=["https://seu-frontend.vercel.app"]

# Opcional: Usar PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/db
```

#### Upgrade para PostgreSQL (Recomendado)

SQLite não é recomendado para produção no Render.

1. **No Dashboard Render**, crie um PostgreSQL Database
2. **Copie a URL** de conexão (Internal Database URL)
3. **Atualize** a variável `DATABASE_URL` no seu Web Service

### Passo 4: Testar o Deploy

```bash
# Health check
curl https://seu-app.onrender.com/health

# Documentação
# Abra: https://seu-app.onrender.com/docs
```

### Troubleshooting

**Erro: Application failed to start**
- Verifique os logs no Dashboard do Render
- Confirme que todas as variáveis obrigatórias estão configuradas

**Erro: Database connection failed**
- Se usando PostgreSQL, verifique a DATABASE_URL
- Para SQLite, certifique-se de que o caminho está correto

**Erro: CORS blocked**
- Adicione seu domínio frontend em `CORS_ORIGINS`
- Formato: `["https://exemplo.com","https://outro.com"]`

---

## 🧪 Testes

```bash
# Instalar dependências de teste (quando disponível)
pip install -r requirements-test.txt

# Rodar testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=app --cov-report=html
```

### Testar Endpoints Manualmente

```bash
# Cadastro
curl -X POST "http://localhost:8000/cadastro" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "teste",
    "senha": "Teste@123",
    "email": "teste@example.com",
    "tag": "cliente",
    "plan": "trial"
  }'

# Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email_ou_login": "teste@example.com",
    "senha": "Teste@123"
  }'

# Buscar usuário autenticado
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🛡️ Segurança

### Práticas Implementadas

- ✅ **Senhas hashadas** com bcrypt (custo 12 rounds)
- ✅ **JWT assinado** com HS256
- ✅ **Rate limiting** para prevenir brute force
- ✅ **Validação de entrada** em múltiplas camadas
- ✅ **CORS configurável** por ambiente
- ✅ **Secrets management** via variáveis de ambiente

### Recomendações para Produção

1. **Use PostgreSQL** ao invés de SQLite
2. **Gere chaves secretas únicas** (nunca use as padrões)
3. **Configure HTTPS** (Render faz isso automaticamente)
4. **Monitore logs** regularmente
5. **Implemente backup** do banco de dados
6. **Use environment-specific configs**

### Reportar Vulnerabilidades

Se encontrar uma vulnerabilidade, por favor **NÃO** abra uma issue pública. 
Envie um email para: security@example.com

---

## 📊 Performance

### Métricas Esperadas

- **Tempo de resposta**: < 100ms (endpoints simples)
- **Rate limit**: Configurável por endpoint
- **Throughput**: 1000+ req/s (com Uvicorn + workers)

### Otimizações

- Connection pooling (PostgreSQL)
- Índices no banco de dados
- Cache de queries frequentes (futuro)
- CDN para assets estáticos (se aplicável)

---

## 🗺️ Roadmap

### v1.1 (Próxima Release)
- [ ] Refresh tokens
- [ ] Email verification
- [ ] Password reset
- [ ] 2FA (Two-Factor Authentication)

### v1.2
- [ ] Paginação na listagem
- [ ] Filtros avançados
- [ ] Cache com Redis
- [ ] Logs estruturados

### v2.0
- [ ] Microserviços
- [ ] GraphQL endpoint
- [ ] Webhooks
- [ ] Admin dashboard

---

## 🤝 Contribuição

Contribuições são bem-vindas! Siga estas etapas:

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add: nova feature incrível'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Convenção de Commits

```
feat: Nova funcionalidade
fix: Correção de bug
docs: Documentação
style: Formatação
refactor: Refatoração
test: Testes
chore: Manutenção
```

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---

## 👨‍💻 Autores

- **Diego** - [@Dieghonm](https://github.com/Dieghonm)
- **Cava** - Contribuidor
- **Tiago** - Contribuidor

---

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework incrível
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM poderoso
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Validação de dados
- [Render](https://render.com/) - Plataforma de hosting

---

## 📞 Suporte

- 📧 Email: support@backbase.com
- 💬 Discord: [Link do servidor]
- 🐛 Issues: [GitHub Issues](https://github.com/Dieghonm/BackBase/issues)

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela!**

Made with ❤️ by BackBase Team

</div>

# Guia de Execução do Projeto BackBase (FastAPI) 
```bash
git clone git@github.com:Dieghonm/BackBase.git
cd BackBase
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Executar a aplicação
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Encerrar o servidor
Pressione CTRL + C para parar a execução.
