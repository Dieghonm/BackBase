# 🚀 Roadmap de Melhorias - BackBase API (Checkpoints)

---

## 🔥 **PRIORIDADE MÁXIMA (Implementar AGORA)**

### **Checkpoint 1: Variáveis de Ambiente**
- [ ] Criar arquivo `.env` na raiz do projeto
- [ ] Instalar `python-dotenv` no requirements.txt
- [ ] Criar `app/config.py` com classe Settings
- [ ] Mover `DATABASE_URL` para .env
- [ ] Adicionar `SECRET_KEY` para JWT
- [ ] Adicionar `.env` no .gitignore
- [ ] Testar se variáveis estão carregando corretamente
- [ ] **✅ Checkpoint 1 Concluído**

### **Checkpoint 2: JWT Authentication**
- [ ] Instalar `python-jose` no requirements.txt
- [ ] Criar `app/utils/jwt_auth.py`
- [ ] Implementar `create_access_token()`
- [ ] Implementar `verify_token()`
- [ ] Modificar endpoint `/login` para retornar JWT
- [ ] Criar schema `TokenResponse` 
- [ ] Testar geração e validação de token
- [ ] **✅ Checkpoint 2 Concluído**

### **Checkpoint 3: Rate Limiting**
- [ ] Instalar `slowapi` no requirements.txt
- [ ] Configurar limiter no main.py
- [ ] Adicionar rate limit no `/login` (5/minuto)
- [ ] Adicionar rate limit no `/cadastro` (3/minuto)
- [ ] Testar limitação funcionando
- [ ] Criar handler personalizado para rate limit
- [ ] **✅ Checkpoint 3 Concluído**

### **Checkpoint 4: Logging Estruturado**
- [ ] Criar `app/utils/logger.py`
- [ ] Configurar formatação de logs
- [ ] Adicionar logs em operações críticas
- [ ] Criar rotação de logs
- [ ] Testar logs sendo gravados
- [ ] Configurar níveis de log (INFO, WARNING, ERROR)
- [ ] **✅ Checkpoint 4 Concluído**

---

## ⚡ **PRIORIDADE ALTA (Próximas 2 semanas)**

### **Checkpoint 5: Middleware de Autenticação**
- [ ] Criar `app/utils/auth_middleware.py`
- [ ] Implementar `get_current_user()`
- [ ] Proteger endpoint `GET /usuarios` com JWT
- [ ] Proteger endpoint `PUT /usuarios/{id}` com JWT
- [ ] Proteger endpoint `DELETE /usuarios/{id}` com JWT
- [ ] Testar acesso negado sem token
- [ ] Testar acesso permitido com token válido
- [ ] **✅ Checkpoint 5 Concluído**

### **Checkpoint 6: Paginação**
- [ ] Criar schema `PaginationParams`
- [ ] Criar schema `PaginatedResponse`
- [ ] Modificar `listar_usuarios()` para aceitar paginação
- [ ] Implementar `listar_usuarios_paginado()` no CRUD
- [ ] Adicionar metadata (total, página, páginas totais)
- [ ] Testar paginação com diferentes tamanhos
- [ ] **✅ Checkpoint 6 Concluído**

### **Checkpoint 7: Índices no Banco**
- [ ] Adicionar índice em `Usuario.login`
- [ ] Adicionar índice em `Usuario.email`
- [ ] Adicionar índice em `Usuario.credencial`
- [ ] Adicionar índice em `Usuario.created_at`
- [ ] Criar migração se necessário
- [ ] Testar performance de consultas
- [ ] **✅ Checkpoint 7 Concluído**

### **Checkpoint 8: Health Check Avançado**
- [ ] Criar endpoint `/health/detailed`
- [ ] Verificar conexão com banco de dados
- [ ] Adicionar informações de uptime
- [ ] Adicionar informações de versão
- [ ] Incluir status de dependências
- [ ] Testar em diferentes cenários
- [ ] **✅ Checkpoint 8 Concluído**

---

## 💡 **PRIORIDADE MÉDIA (Próximo mês)**

### **Checkpoint 9: Soft Delete**
- [ ] Adicionar coluna `deleted_at` no modelo Usuario
- [ ] Adicionar coluna `is_active` no modelo Usuario
- [ ] Modificar `deletar_usuario()` para soft delete
- [ ] Modificar consultas para filtrar usuários ativos
- [ ] Criar endpoint para restaurar usuários
- [ ] Testar soft delete funcionando
- [ ] **✅ Checkpoint 9 Concluído**

### **Checkpoint 10: Testes Unitários**
- [ ] Instalar `pytest` e `httpx`
- [ ] Criar pasta `tests/`
- [ ] Criar `test_auth.py` para autenticação
- [ ] Criar `test_usuarios.py` para CRUD
- [ ] Criar fixtures para dados de teste
- [ ] Configurar banco de teste
- [ ] Executar testes e verificar cobertura
- [ ] **✅ Checkpoint 10 Concluído**

### **Checkpoint 11: CORS Mais Seguro**
- [ ] Configurar origins específicos para produção
- [ ] Remover wildcard "*" do CORS
- [ ] Configurar headers permitidos específicos
- [ ] Configurar métodos permitidos específicos
- [ ] Testar CORS em ambiente de produção
- [ ] **✅ Checkpoint 11 Concluído**

### **Checkpoint 12: Métricas**
- [ ] Criar sistema de contadores
- [ ] Implementar middleware para métricas
- [ ] Criar endpoint `/metrics`
- [ ] Rastrear requests por método
- [ ] Rastrear tempo de resposta
- [ ] Rastrear usuários ativos
- [ ] **✅ Checkpoint 12 Concluído**

---

## 🚀 **PRIORIDADE BAIXA (Quando tiver tempo)**

### **Checkpoint 13: Docker**
- [ ] Criar `Dockerfile`
- [ ] Criar `docker-compose.yml`
- [ ] Configurar PostgreSQL no Docker
- [ ] Testar build da imagem
- [ ] Testar execução em container
- [ ] Documentar comandos Docker
- [ ] **✅ Checkpoint 13 Concluído**

### **Checkpoint 14: Timestamps Automáticos**
- [ ] Adicionar coluna `updated_at` no modelo
- [ ] Configurar auto-update do timestamp
- [ ] Testar timestamps sendo atualizados
- [ ] Adicionar no schema de resposta
- [ ] **✅ Checkpoint 14 Concluído**

---

## 📋 **TODOLIST SEQUENCIAL (Front-end + Back-end)**

### **Front-end**
- [x] Criar formulário de cadastro/login com campos necessários
- [x] Implementar validação básica no formulário
- [ ] **Checkpoint A:** Integrar com JWT do Back-end
  - [ ] Modificar função de envio para receber JWT
  - [ ] Armazenar JWT no localStorage
  - [ ] Implementar interceptor para adicionar token nos headers
  - [ ] **✅ Checkpoint A Concluído**

### **Back-end (Melhorias de Integração)**
- [x] Endpoint de cadastro/login básico funcionando
- [ ] **Checkpoint B:** Implementar JWT nos endpoints existentes
  - [ ] Modificar `/login` para retornar JWT
  - [ ] Validar formato de retorno compatível com Front-end
  - [ ] Testar integração com Front-end
  - [ ] **✅ Checkpoint B Concluído**

- [ ] **Checkpoint C:** Proteger endpoints sensíveis
  - [ ] Aplicar middleware de autenticação
  - [ ] Verificar se usuário logado pode acessar seus próprios dados
  - [ ] Implementar autorização por roles (admin, cliente, tester)
  - [ ] **✅ Checkpoint C Concluído**

### **Front-end (Continuação)**
- [ ] **Checkpoint D:** Gerenciamento de sessão
  - [ ] Implementar verificação de token válido
  - [ ] Auto-renovação de token próximo ao vencimento
  - [ ] Redirecionamento automático se token expirado
  - [ ] **✅ Checkpoint D Concluído**

- [ ] **Checkpoint E:** UX/UI de autenticação
  - [ ] Feedback visual durante loading
  - [ ] Mensagens de erro amigáveis
  - [ ] Implementar logout com limpeza de dados
  - [ ] Tela de perfil para alterar dados
  - [ ] **✅ Checkpoint E Concluído**

### **Integração Final**
- [ ] **Checkpoint F:** Testes End-to-End
  - [ ] Testar fluxo completo: cadastro → login → acesso → logout
  - [ ] Testar cenários de erro
  - [ ] Testar em diferentes browsers
  - [ ] Performance testing
  - [ ] **✅ Checkpoint F Concluído**

---

## 🎯 **MARCO DE PROGRESSO**

### **Sprint 1 (Semana 1-2): Segurança Core**
- [ ] Checkpoints 1-4 concluídos
- [ ] JWT funcionando
- [ ] Rate limiting ativo
- [ ] Logs estruturados
- [ ] **🏆 Sprint 1 Concluída**

### **Sprint 2 (Semana 3-4): Proteção e Performance** 
- [ ] Checkpoints 5-8 concluídos  
- [ ] Endpoints protegidos
- [ ] Paginação implementada
- [ ] Performance otimizada
- [ ] **🏆 Sprint 2 Concluída**

### **Sprint 3 (Mês 2): Qualidade e Robustez**
- [ ] Checkpoints 9-12 concluídos
- [ ] Testes implementados
- [ ] Soft delete funcionando
- [ ] Métricas coletadas
- [ ] **🏆 Sprint 3 Concluída**

### **Sprint 4 (Quando possível): DevOps**
- [ ] Checkpoints 13-14 concluídos
- [ ] Docker configurado
- [ ] Deploy automatizado
- [ ] **🏆 Projeto Enterprise-Ready! 🚀**

