# AutoChat Pro

Plataforma de automação de atendimento WhatsApp e Telegram com IA.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11 + FastAPI + MongoDB + Redis |
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| IA | GLM (LLM API) |
| WhatsApp | Evolution API v2 (Baileys) |
| Telegram | Telegram Bot API (webhook direto via httpx) |
| Infra | Docker Compose + Cloudflare Tunnel |

## Portas

| Serviço | Porta | Container |
|---------|-------|-----------|
| Frontend (nginx) | `5174` | autochat-frontend |
| Backend (FastAPI) | `8100` → container `8000` | autochat-backend |
| Evolution API | `8090` → container `8080` | autochat-evolution |
| MongoDB | `27018` | autochat-mongodb |
| PostgreSQL (Evo) | interno `5432` | autochat-evolution-db |
| Redis | `6380` | autochat-redis |
| Postfix (email) | `25` / `587` | autochat-postfix |

## Credenciais de Teste

- **Login:** admin@autochat.com / Admin@123
- **MongoDB:** mongodb://admin:admin123@localhost:27018/?authSource=admin
- **Evolution API Key:** `429683C4C977415CAAFCCE10F7D57E11` (mesma no docker-compose e .env)

## Como Rodar

```bash
cd /root/projetoclaude
docker compose up -d
```

## Endpoints Úteis

- Backend health: http://localhost:8100/health
- Backend docs: http://localhost:8100/docs
- Frontend: http://localhost:5174
- Evolution API: http://localhost:8090

### Backend API v1

| Grupo | Endpoints |
|-------|-----------|
| Auth | POST /auth/login, /auth/register, GET /auth/me |
| Bots | POST /bots, GET /bots, GET /bots/{id}, PUT /bots/{id}, DELETE /bots/{id}, POST /bots/{id}/pause, POST /bots/{id}/resume |
| WhatsApp | POST /whatsapp/connect/qrcode, POST /whatsapp/connect/phone, GET /whatsapp/instances/{name}/status, POST /whatsapp/webhook/{name} |
| Dashboard | GET /dashboard/metrics, GET /conversations |
| Contatos | GET /contacts, DELETE /contacts/{id} |
| Planos | GET /plans, GET /plan/current, POST /plan/upgrade |

### Rotas Frontend

| Rota | Página |
|------|-------|
| /dashboard | Dashboard com stats e bots |
| /add-bot | Conectar WhatsApp (QR/phone) ou Telegram (token) |
| /bots | Listar e gerenciar bots |
| /bots/:botId/config | Configurar bot (mensagens, horário, IA) |
| /conversations | Lista de conversas |
| /contacts | Lista de contatos/leads |
| /pricing | Planos e preços |
| /automations | (em breve) |
| /settings | Configurações (Perfil, Segurança, Notificações) |

## Arquitetura (DDD)

```
backend/src/
├── domain/          # Entidades e interfaces de repositórios
├── application/     # Casos de uso, DTOs, serviços, stores
├── infrastructure/   # MongoDB, repos, Evolution API client
├── api/
│   ├── v1/endpoints/  # Endpoints REST
│   └── middleware/     # Auth, CORS, etc
└── shared/          # Config, utils, exceptions

frontend/src/
├── presentation/    # Páginas e componentes UI
├── infrastructure/  # HTTP client e services
├── application/     # Hooks e stores (zustand)
└── shared/          # Types e utilitários
```

## Páginas Frontend

`HomePage` · `LoginPage` · `RegisterPage` · `DashboardPage` · `AddBotPage` · `BotConfigPage` · `BotsPage` · `ConversationsPage` · `ContactsPage` · `PricingPage` · `ConfirmEmailPage` · `ConfirmPhonePage` · `ForgotPasswordPage` · `ResetPasswordPage`

## Integração WhatsApp (Evolution API v2)

### Endpoints corretos da Evolution API v2
- Criar instância: `POST /instance/create` com body `{"instanceName": "...", "qrcode": false}`
- Phone pairing: `GET /instance/connect/{instanceName}?number={ddi+ddd+numero}`
  - Retorna `{"pairingCode": "ABC12345", "code": "...", "base64": "...", "count": 1}`
- Status da conexão: `GET /instance/connectionState/{instanceName}`
  - Retorna `{"instance": {"instanceName": "...", "state": "connecting|open|close"}}`
- QR Code: `POST /instance/restart/{instanceName}` (retorna base64)
- Listar instâncias: `GET /instance/fetchInstances`
- Deletar instância: `DELETE /instance/delete/{instanceName}`
- Logout: `DELETE /instance/logout/{instanceName}`
- Enviar texto: `POST /message/sendText/{instanceName}` com `{"number": "...", "text": "..."}`
- Enviar mídia: `POST /message/sendMedia/{instanceName}` com `{"number": "...", "mediatype": "image", "media": "url"}`

### Formato de erros do backend
Sempre usar `{erro: {codigo: "...", mensagem: "..."}}` (português).
O handler global em `main.py` formata automaticamente quando se usa `BaseAppException`.

## Bugs Corrigidos

### Sessão 2026-06-01 #1 (inicial)
1. bcrypt incompatível com passlib → substituído por bcrypt direto
2. Formato de erro inconsistente (inglês vs português) → padronizado
3. timedelta não importado → adicionado
4. CORS restrito a IP específico → adicionado localhost/127.0.0.1
5. TypeScript errors no frontend → corrigidos
6. Seed de usuário de teste → adicionado

### Sessão 2026-06-01 #2 (WhatsApp)
7. **API Key inconsistente** entre docker-compose (`evolution_api_key_secret...`) e backend `.env` (`429683...`) → padronizado
8. **Phone pairing endpoint errado**: usava `POST /instance/connect/{name}` com body, Evolution API v2 exige `GET /instance/connect/{name}?number={phone}` → corrigido em `evolution_service.py`
9. **Campo de pairingCode errado**: código lia `result.get("code")` mas Evolution API retorna `pairingCode` → corrigido
10. **connectionState aninhado**: código lia `info.get("state")` mas Evolution API retorna `info["instance"]["state"]` → corrigido
11. **check_phone_pairing endpoint inexistente**: usava `/baileys/auth/login/phone/{name}` → mudado para `/instance/connectionState/{name}`
12. **Número sem DDI no frontend**: input só tinha DDD+número mas não adicionava 55 → corrigido em AddBotPage.tsx
13. **Formato de erro dos endpoints WhatsApp**: `{error: {code, message}}` → `{erro: {codigo, mensagem}}`

### Sessão 2026-06-01 #3 — Phone pairing robustez
14. **pairingCode null em reconexão**: instância presa em connecting não gerava novo código → backend agora deleta e recria instância em estado close/connecting antes de reconectar
15. **Tela presa em "Aguardando conexão"**: polling nunca parava → adicionado detecção de disconnected/error + timeout de 3 min
16. **Sem feedback de expiração**: usuário não sabia quanto tempo tinha → adicionado timer visual de 3 min com contagem regressiva (fica vermelho nos últimos 30s)
17. **pairingCode null sem erro**: backend retornava null silenciosamente → agora retorna erro 503 com mensagem clara

### Sessão 2026-06-03 #4 — Auditoria P0
18. **Senha do admin não funciona**: seed pula recriação se usuário existe, hash ficava desatualizado → seed agora sempre atualiza password_hash + role do admin
19. **Registro falha com duplicate key `phone:null`**: `_user_to_document` incluía `phone: null` explicitamente, sparse index só permite um null → campos opcionais (phone, avatar) agora só incluídos quando têm valor; index recriado com cleanup
20. **Automações UUID vs ObjectId**: `bot_id` definido como `UUID` no domínio mas bots usam `ObjectId` (24 hex chars) → mudado para `str` em toda a cadeia: entidade, interface, use cases (create, list, update, delete, toggle) e repositório
21. **Role "admin" não mapeada**: `_document_to_user` e `_user_to_document` ignoravam campo `role` → mapeamento adicionado, JWT agora contém role correto
22. **Segredos hardcodados no docker-compose**: MongoDB pass, Evolution API key e PostgreSQL credenciais → substituídos por `${VAR:-default}` com `.env` na raiz; `backend/.env` removido do git tracking

### Sessão 2026-06-03 #5 — P1 (Segurança + Testes)
23. **Rate limiting em auth**: middleware `rate_limit.py` com Redis (sliding window) nos endpoints login, register e refresh — 10 req/min login/register, 30/min refresh
24. **Testes de domínio**: 20 testes pytest cobrindo Usuario, RegraAutomacao, ConfiguracaoPlano (condições, ativação, limites, trial)

### Sessão 2026-06-03 #6 — P2 (Limpeza + Config)
25. **Código morto removido**: módulo analytics completo (entidade, repo, impl, índices, imports em __init__.py) — nunca foi usado
26. **ENVIRONMENT sync**: backend/.env corrigido para `production`; FRONTEND_URL atualizado para domínio real; `.env.example` já existente
27. **Dependabot**: configurado para pip (backend), npm (frontend) e Docker (raiz) — scanner automático de dependências
28. **Contacts CRUD**: verificado que já está implementado corretamente (repository faz queries reais no MongoDB)

### Sessão 2026-06-03 #7 — P3 (Hardening)
29. **Token blacklist no Redis**: logout agora invalida token via blacklist (hash SHA256 + TTL); middleware auth verifica blacklist antes de autorizar
30. **Complexidade de senha**: registro e reset exigem mín 8 chars + 1 maiúscula + 1 minúscula + 1 número + 1 especial
31. **Account lockout**: 5 tentativas falhas de login bloqueia conta por 15 min (Redis); reset em login bem-sucedido
32. **Headers de segurança**: middleware HTTP com X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy, HSTS (produção)
33. **Limite de bots do plano**: create_bot agora busca plano do usuário e verifica max_bots real (não mais hardcoded 10)
34. **Proteção ReDoS**: regex nas automações limitado a 200 chars, padrões perigosos bloqueados, timeout de 0.5s na execução

## Progresso

- ✅ FASE 1-2: Infraestrutura e autenticação
- ✅ FASE 3: Modelos de dados (DDD)
- ✅ FASE 4: Integração WhatsApp via Evolution API (QR + phone pairing)
- ✅ FASE 4.5: Persistência de bots e fluxo pós-conexão
- ✅ FASE 5: Integração Telegram — TelegramService, webhook, MessageProcessor adaptado
- ✅ FASE 6: Integração IA (GLM) — GLMService, MessageProcessor, webhook receiver
- ✅ FASE 7: Conversas e métricas — Dashboard metrics, ConversationsPage
- ✅ FASE 8: Contatos/Leads — Entidade Contato, repositório, endpoints, ContactsPage
- ✅ FASE 9: Planos e Billing — Free/Basic/Pro, upgrade, PricingPage
- ✅ FASE 10: Automações — CRUD regras, MessageProcessor integrado
- ✅ FASE 11: LLM Avançado — Multi-provider, streaming SSE, contexto conversa
- ✅ FASE 12: Settings Page — Perfil, Segurança, Notificações

## Fluxo completo implementado

### WhatsApp
```
Usuário conecta WhatsApp → Salva bot no MongoDB (user_id) → Redireciona Dashboard
                                                                ↓
                                                    Dashboard mostra bot conectado
                                                                ↓
                                                    Configurar prompt IA, saudação, horário
                                                                ↓
                                                    Mensagens chegam via webhook (Evolution API)
                                                                ↓
                                                    MessageProcessor busca config do bot
                                                                ↓
                                                    Verifica horário de funcionamento
                                                                ↓
                                                    Gera resposta com GLM (ou msg padrão)
                                                                ↓
                                                    Envia resposta automática via WhatsApp
```

### Telegram
```
Usuário insere token do @BotFather → Valida (getMe) → Salva bot no MongoDB
                                                                ↓
                                        Setup webhook no Telegram → autochat.rodney.website/api/v1/telegram/webhook/{token}
                                                                ↓
                                                    Dashboard mostra bot conectado
                                                                ↓
                                                    Mensagens chegam via webhook (Telegram Bot API)
                                                                ↓
                                                    MessageProcessor busca config pelo bot_token
                                                                ↓
                                                    Verifica horário → Automações → LLM GLM
                                                                ↓
                                                    Envia resposta automática via Telegram API
```

## Arquivos criados nesta sessão

### FASE 4.5
- `frontend/src/presentation/pages/BotConfigPage.tsx` — Config do bot (3 tabs: Mensagens, Horário, IA)
- `frontend/src/presentation/pages/BotsPage.tsx` — Listagem de bots com cards e ações
- `frontend/src/App.tsx` — Rotas `/bots` e `/bots/:botId/config`

### FASE 5
- `backend/src/infrastructure/external_services/llm/__init__.py` — Módulo LLM
- `backend/src/infrastructure/external_services/llm/glm_service.py` — Cliente GLM (OpenAI-compatible)
- `backend/src/application/services/message_processor.py` — Processa mensagens webhook → IA → resposta
- `backend/src/api/v1/endpoints/whatsapp.py` — Webhook receiver atualizado com MessageProcessor
- `backend/src/main.py` — MessageProcessor inicializado no startup

### FASE 6
- `backend/src/api/v1/endpoints/dashboard.py` — GET /dashboard/metrics + GET /conversations
- `backend/src/infrastructure/repositories/conversation_repository_impl.py` — Todos métodos abstratos implementados
- `frontend/src/infrastructure/api/conversations.service.ts` — API client de conversas e dashboard
- `frontend/src/presentation/pages/ConversationsPage.tsx` — Lista de conversas com filtros

### FASE 9 — Automações
- `backend/src/infrastructure/repositories/automation_rule_repository_impl.py` — MongoDB repo completo
- `backend/src/application/dto/automation_rule_dto.py` — CriarRegraRequest, AtualizarRegraRequest, RegraResponse
- `backend/src/application/use_cases/*_automation_rule_use_case.py` — CRUD + toggle
- `backend/src/api/v1/endpoints/automations.py` — POST/GET/PUT/DELETE /automations + toggle
- `backend/src/application/services/message_processor.py` — Integrado: avalia regras antes de chamar LLM
- `frontend/src/presentation/pages/AutomationsPage.tsx` — CRUD de regras com condition/action builder
- `frontend/src/infrastructure/api/automations.service.ts` — API client

### FASE 5 — Telegram
- `backend/src/infrastructure/external_services/telegram/__init__.py` — Singleton factory
- `backend/src/infrastructure/external_services/telegram/telegram_service.py` — Webhook, send, getMe (httpx)
- `backend/src/api/v1/endpoints/telegram.py` — Webhook receiver, validate-token, setup/delete webhook
- `backend/src/application/services/message_processor.py` — `process_telegram_message()` com LLM + automações
- `frontend/src/presentation/pages/AddBotPage.tsx` — Selector WhatsApp | Telegram, token input, validação
- `frontend/src/infrastructure/api/telegram.service.ts` — validateToken, setupWebhook, deleteWebhook

### FASE 12 — Settings
- `frontend/src/presentation/pages/SettingsPage.tsx` — Perfil, Segurança, Notificações

### FASE 10 — LLM Avançado
- `backend/src/infrastructure/external_services/llm/llm_service.py` — Multi-provider (GLM, OpenAI, Anthropic, Ollama)
- `backend/src/application/services/conversation_context.py` — Histórico de conversa pra contexto LLM
- `backend/src/api/v1/endpoints/chat.py` — /chat/stream (SSE), /chat/complete, /chat/providers
- `backend/src/application/services/message_processor.py` — Usa LLMService + ConversationContext
- `frontend/src/presentation/pages/BotConfigPage.tsx` — Provider/model/temperature/context config

## Deploy
- **URL:** https://autochat.rodney.website (frontend)
- **API:** https://autochat.rodney.website/api/v1/
- **Swagger:** https://autochat.rodney.website/docs
- **Docker:** 7 containers (backend, frontend, mongodb, redis, postfix, evolution-api, evolution-db)
- **Nginx:** Reverse proxy em localhost:80 → Cloudflare tunnel wildcard
- **Git:** https://github.com/rodneysilva/autochat-pro.git

## Preferências

- Idioma: sempre português
- Comunicação: direta e prática
- Dark mode: implementado (ThemeProvider + Tailwind dark classes)
- Layout: mobile-first responsivo
- Sempre guiar o usuário com hints e exemplos nas interfaces
