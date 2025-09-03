## 📁 **backbase/run.py**
**Responsabilidade:** Ponto de entrada do projeto
- Configura o path para encontrar a pasta `app`
- Importa e executa a função `main()` do módulo principal
- Permite executar o projeto com `python run.py`

## 📁 **backbase/app/__init__.py**
**Responsabilidade:** Transformar a pasta em módulo Python
- Indica ao Python que `app` é um pacote/módulo
- Permite importações entre os arquivos da pasta
- Pode conter inicializações globais do módulo (se necessário)

## 📁 **backbase/app/database.py**
**Responsabilidade:** Configuração e conexão com banco de dados
- Define a string de conexão (`DATABASE_URL`)
- Configura o engine SQLAlchemy
- Cria o `SessionLocal` para sessões do banco
- Define a classe `Base` para os modelos
- Função `criar_tabelas()` - verifica/cria o banco automaticamente
- Função `get_db()` - dependency injection para fornecer sessões

## 📁 **backbase/app/models.py**
**Responsabilidade:** Definir modelos/entidades do banco (ORM)
- Contém as classes que representam tabelas do banco
- Classe `Usuario` - define estrutura da tabela usuarios
- Mapeia colunas, tipos de dados, constraints
- Herda de `Base` do SQLAlchemy
- **É o "M" do padrão MVC (Model)**

## 📁 **backbase/app/schemas.py**
**Responsabilidade:** Definir contratos de entrada/saída da API
- Modelos Pydantic para validação de dados
- `UsuarioCreate` - valida dados de entrada (requests)
- `UsuarioResponse` - define formato de saída (responses)
- Validações automáticas (email, tipos, campos obrigatórios)
- Serialização/deserialização JSON ↔ Python

## 📁 **backbase/app/crud.py**
**Responsabilidade:** Operações de banco de dados (Business Logic)
- **C**reate - `criar_usuario()`
- **R**ead - `listar_usuarios()`, `buscar_usuario_por_id()`, `buscar_usuario_por_email()`
- **U**pdate - `atualizar_usuario()`
- **D**elete - `deletar_usuario()`
- Lógicas específicas como `gerar_credencial()`
- Camada entre as rotas e o banco de dados

## 📁 **backbase/app/main.py**
**Responsabilidade:** Rotas e endpoints da API (Controller)
- Configuração da aplicação FastAPI
- Define todos os endpoints (`@app.post`, `@app.get`, etc.)
- Gerencia requests/responses HTTP
- Chama funções do `crud.py`
- Tratamento de erros HTTP
- **É o "C" do padrão MVC (Controller)**

---

## 🏗️ **Arquitetura (padrão em camadas):**
```
┌─────────────────┐
│   main.py       │ ← API/Controller (HTTP)
│   (FastAPI)     │
├─────────────────┤
│   crud.py       │ ← Business Logic
│   (operações)   │
├─────────────────┤
│   models.py     │ ← Data Models (ORM)
│   (SQLAlchemy)  │
├─────────────────┤
│   database.py   │ ← Database Config
│   (conexão)     │
└─────────────────┘
```

**schemas.py** atua como "contrato" entre as camadas, garantindo que os dados fluam corretamente entre elas.

Essa separação torna o código:
- **Mais organizado** - cada arquivo tem uma função específica
- **Mais testável** - pode testar cada camada isoladamente  
- **Mais reutilizável** - pode usar `crud.py` em outros lugares
- **Mais manutenível** - mudanças em uma camada não afetam outras