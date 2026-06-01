# AutoChat Pro

Plataforma de automação de atendimento WhatsApp com IA.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11 + FastAPI + MongoDB + Redis |
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| IA | GLM (LLM API) |
| WhatsApp | Evolution API v2 (Baileys) |
| Infra | Docker Compose |

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

`HomePage` · `LoginPage` · `RegisterPage` · `DashboardPage` · `AddBotPage` · `ConfirmEmailPage` · `ConfirmPhonePage` · `ForgotPasswordPage` · `ResetPasswordPage`

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

## Progresso

## Progresso

- ✅ FASE 1-2: Infraestrutura e autenticação
- ✅ FASE 3: Modelos de dados (DDD)
- ✅ FASE 4: Integração WhatsApp via Evolution API (QR + phone pairing)
- 🔜 **FASE 4.5: Persistência de bots e fluxo pós-conexão** (PRÓXIMO PASSO — ver abaixo)
- 🔜 FASE 5: Conectar IA (GLM) aos bots
- 🔜 FASE 6: Dashboard com métricas
- 🔜 FASE 7: Gerenciamento de contatos/leads
- 🔜 FASE 8: Planos e billing

## Próximo Passo Importante — FASE 4.5

O fluxo atual de WhatsApp está **incompleto**:
- ✅ Conexão com Evolution API funciona (QR + phone pairing)
- ❌ Bot NÃO é salvo no MongoDB após conexão
- ❌ Não há vínculo entre instância WhatsApp e usuário logado
- ❌ Dashboard não lista bots (não há dados para listar)
- ❌ Após conectar, volta para página de adicionar bot sem continuidade

### O que precisa ser feito:
1. **Modelo Bot** no domain — entidade Bot com: name, instance_name, phone, user_id, status, config_ia, created_at
2. **Repositório Bot** no infrastructure — CRUD no MongoDB (collection `bots`)
3. **Use case CreateBot** — após conexão WhatsApp bem-sucedida, salva bot vinculado ao user
4. **Endpoint POST /whatsapp/connect/phone** → após sucesso, cria registro no MongoDB
5. **Endpoint GET /bots** — lista bots do usuário logado
6. **Dashboard atualizado** — mostra cards com bots conectados, status em tempo real, ações (configurar, pausar, desconectar)
7. **Página de configuração do bot** — definir prompt da IA, mensagens de saudação, horário de funcionamento
8. **Webhook receiver** — quando mensagem chegar na Evolution API, buscar config do bot e responder com IA (GLM)

### Fluxo completo alvo:
```
Usuário conecta WhatsApp → Salva bot no MongoDB (user_id) → Redireciona Dashboard
                                                                ↓
                                                    Dashboard mostra bot conectado
                                                                ↓
                                                    Configurar prompt IA, saudação
                                                                ↓
                                                    Mensagens chegam via webhook
                                                                ↓
                                                    Bot responde automaticamente com GLM
```

## Preferências

- Idioma: sempre português
- Comunicação: direta e prática
- Dark mode: implementado (ThemeProvider + Tailwind dark classes)
- Layout: mobile-first responsivo
