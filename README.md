# API de Gerenciamento de Usuários

API FastAPI para gerenciamento de usuários com validações completas e arquitetura organizada.

## 🚀 Funcionalidades

- ✅ Cadastro de usuários com validações completas
- ✅ Listagem de usuários
- ✅ Busca de usuários por ID
- ✅ Validação de dados de entrada
- ✅ Geração de credenciais seguras
- ✅ Tratamento de erros detalhado

## 📁 Estrutura do Projeto

```
projeto/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   └── usuario.py
│   ├── schemas/                # Schemas Pydantic
│   │   ├── __init__.py
│   │   └── usuario.py
│   ├── database/               # Configuração do banco
│   │   ├── __init__.py
│   │   └── connection.py
│   ├── services/               # Lógica de negócio
│   │   ├── __init__.py
│   │   └── usuario_service.py
│   ├── utils/                  # Utilitários
│   │   ├── __init__.py
│   │   ├── validators.py       # Validadores
│   │   └── security.py         # Funções de segurança
│   └── routes/                 # Endpoints da API
│       ├── __init__.py
│       └── usuario_routes.py
├── requirements.txt
└── README.md
```

## 🔧 Instalação

1. **Clone o projeto** (se aplicável)

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação:**
```bash
uvicorn app.main:app --reload
```

A API estará disponível em: `http://localhost:8000`

## 📚 Documentação da API

Após executar a aplicação, acesse:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔍 Validações Implementadas

### Cadastro de Usuário (`POST /usuarios/cadastro`)

- **ID**: Gerado automaticamente (próximo ID disponível)
- **Login**: 
  - Deve ter entre 3-50 caracteres
  - Apenas letras, números e underscore
  - Deve ser único
  - Convertido para lowercase
- **Email**: 
  - Formato válido (usando EmailStr do Pydantic)
  - Deve ser único
  - Convertido para lowercase
- **Tag**: 
  - Deve ser uma das opções: `admin`, `tester`, `usuario`
  - Padrão: `usuario`
- **Plan**: 
  - Opcional
  - Deve ser uma das opções: `trial`, `mensal`, `trimestral`, `semestral`
- **Plan_date**: 
  - Gerada automaticamente como data atual (se plan for fornecido)
  - Formato UTC
- **Credencial**: 
  - Gerada automaticamente usando SHA256
  - Baseada no email, data de validade e token aleatório
- **Senha**: 
  - Deve ter pelo menos 6 caracteres
  - ⚠️ Atualmente armazenada em texto plano (implementar hash depois)
- **Created_at**: 
  - Gerado automaticamente como data atual
  - Formato UTC

## 🎯 Endpoints

### `GET /`
Endpoint de teste da API

### `GET /health`
Health check da API

### `POST /usuarios/cadastro`
Cadastra um novo usuário

**Body:**
```json
{
  "login": "usuario123",
  "senha": "minhasenha123",
  "email": "usuario@example.com",
  "tag": "usuario",
  "plan": "mensal"
}
```

**Resposta:**
```json
{
  "sucesso": true,
  "id": 1,
  "credencial": "abc123...",
  "created_at": "2025-01-15T10:30:00Z",
  "message": "Usuário criado com sucesso"
}
```

### `GET /usuarios/`
Lista todos os usuários

### `GET /usuarios/{user_id}`
Busca um usuário específico por ID

## ⚠️ Notas Importantes

1. **Senhas**: Atualmente armazenadas em texto plano. Implementar hash (bcrypt) posteriormente.

2. **Banco de dados**: Usando SQLite por simplicidade. Para produção, considere PostgreSQL ou MySQL.

3. **CORS**: Configurado para aceitar todas as origens. Em produção, especifique domínios específicos.

4. **Tratamento de erros**: Implementado com mensagens detalhadas e códigos HTTP apropriados.

## 🔒 Segurança

- Validação rigorosa de todos os dados de entrada
- Geração de credenciais usando hash SHA256
- Prevenção de duplicação de login e email
- Sanitização de dados (conversão para lowercase)

## 🚀 Como usar

1. **Testar a API:**
```bash
curl http://localhost:8000/
```

2. **Cadastrar um usuário:**
```bash
curl -X POST "http://localhost:8000/usuarios/cadastro" \
-H "Content-Type: application/json" \
-d '{
  "login": "testuser",
  "senha": "123456",
  "email": "test@example.com",
  "tag": "usuario",
  "plan": "trial"
}'
```

3. **Listar usuários:**
```bash
curl http://localhost:8000/usuarios/
```

## 🐛 Tratamento de Erros

A API retorna erros detalhados com códigos HTTP apropriados:

- **400 Bad Request**: Dados inválidos ou duplicados
- **404 Not Found**: Usuário não encontrado
- **500 Internal Server Error**: Erro interno do servidor

**Exemplo de erro:**
```json
{
  "detail": "Erros de validação: Login já está em uso; Email já está em uso"
}
```

## 📈 Próximas Melhorias

- [ ] Implementar hash de senhas com bcrypt
- [ ] Adicionar autenticação JWT
- [ ] Implementar paginação na listagem
- [ ] Adicionar logs detalhados
- [ ] Implementar cache Redis
- [ ] Adicionar testes unitários
- [ ] Dockerizar a aplicação

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.



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
