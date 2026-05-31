# 🔌 API Endpoints - AutoChat Pro

**Documentação completa dos endpoints REST e WebSocket**

---

## Base URL

```
Desenvolvimento: http://localhost:8000/api/v1
Produção: https://api.autochat.pro/api/v1
```

---

## Autenticação

Todos os endpoints (exceto auth) requerem Bearer Token:

```
Authorization: Bearer <jwt_token>
```

---

## 📚 Resumo dos Endpoints

| Categoria | Endpoints | Descrição |
|-----------|-----------|-----------|
| **Auth** | 6 | Login, registro, confirmação |
| **Users** | 4 | Perfil, configurações |
| **Bots** | 8 | CRUD de bots |
| **WhatsApp** | 5 | Conexão WhatsApp |
| **Telegram** | 4 | Conexão Telegram |
| **Conversations** | 7 | Gerenciamento de conversas |
| **Messages** | 4 | Envio/recebimento |
| **Automations** | 6 | Regras de automação |
| **Analytics** | 3 | Métricas e estatísticas |
| **Admin** | 5 | Gestão administrativa |
| **WebSocket** | 1 | Eventos em tempo real |

**Total: 53 endpoints + 1 WebSocket**

---

## 1. Autenticação

### POST /auth/register
Registro de novo usuário

**Request:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "Senha@123",
  "name": "João Silva",
  "phone": "+5511999999999"
}
```

**Response (201):**
```json
{
  "message": "Registration successful",
  "requiresEmailConfirmation": true,
  "requiresPhoneConfirmation": false,
  "userId": "507f1f77bcf86cd799439011"
}
```

---

### POST /auth/login
Login com email e senha

**Request:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "Senha@123"
}
```

**Response (200):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
  "expiresIn": 3600,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "usuario@exemplo.com",
    "name": "João Silva",
    "plan": {
      "type": "free",
      "maxBots": 1
    }
  }
}
```

---

### POST /auth/confirm-email
Confirmação de email

**Request:**
```json
{
  "token": "abc123...",
  "code": "123456"
}
```

**Response (200):**
```json
{
  "message": "Email confirmed successfully"
}
```

---

### POST /auth/confirm-phone
Confirmação de telefone

**Request:**
```json
{
  "phone": "+5511999999999",
  "code": "123456"
}
```

**Response (200):**
```json
{
  "message": "Phone confirmed successfully"
}
```

---

### POST /auth/forgot-password
Solicitar recuperação de senha

**Request:**
```json
{
  "email": "usuario@exemplo.com"
}
```

**Response (200):**
```json
{
  "message": "Password reset email sent"
}
```

---

### POST /auth/reset-password
Redefinir senha

**Request:**
```json
{
  "token": "reset_token_here",
  "password": "NovaSenha@123"
}
```

**Response (200):**
```json
{
  "message": "Password reset successfully"
}
```

---

### POST /auth/refresh-token
Renovar access token

**Request:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "expiresIn": 3600
}
```

---

## 2. Users

### GET /users/me
Obter perfil do usuário atual

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "usuario@exemplo.com",
  "name": "João Silva",
  "phone": "+5511999999999",
  "emailConfirmed": true,
  "phoneConfirmed": true,
  "plan": {
    "type": "basic",
    "maxBots": 3,
    "maxMessagesPerMonth": 5000,
    "expiresAt": "2026-06-30T23:59:59Z",
    "features": ["whatsapp", "telegram", "llm"]
  },
  "createdAt": "2026-05-31T10:00:00Z"
}
```

---

### PUT /users/me
Atualizar perfil

**Request:**
```json
{
  "name": "João Silva Jr.",
  "avatar": "https://..."
}
```

---

### PUT /users/me/password
Alterar senha

**Request:**
```json
{
  "currentPassword": "Senha@123",
  "newPassword": "NovaSenha@456"
}
```

---

## 3. Bots

### GET /bots
Listar bots do usuário

**Query Params:**
- `page`: número da página (default: 1)
- `limit`: itens por página (default: 20)
- `status`: filter by status (optional)

**Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439013",
      "name": "Bot de Atendimento",
      "type": "whatsapp",
      "status": "active",
      "stats": {
        "totalMessages": 1250,
        "totalConversations": 89
      },
      "createdAt": "2026-05-31T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 3,
    "totalPages": 1
  }
}
```

---

### POST /bots
Criar novo bot

**Request:**
```json
{
  "name": "Bot de Atendimento",
  "type": "whatsapp",
  "welcomeMessage": "Olá! Como posso ajudar?"
}
```

**Response (201):**
```json
{
  "id": "507f1f77bcf86cd799439013",
  "name": "Bot de Atendimento",
  "type": "whatsapp",
  "status": "disconnected",
  "createdAt": "2026-05-31T10:00:00Z"
}
```

---

### GET /bots/{id}
Detalhes do bot

---

### PUT /bots/{id}
Atualizar bot

**Request:**
```json
{
  "name": "Novo Nome",
  "welcomeMessage": "Nova mensagem",
  "workingHours": {
    "enabled": true,
    "start": "09:00",
    "end": "18:00"
  }
}
```

---

### DELETE /bots/{id}
Deletar bot

---

### PUT /bots/{id}/pause
Pausar bot

---

### PUT /bots/{id}/resume
Resumir bot

---

### POST /bots/{id}/test
Testar bot (enviar mensagem de teste)

**Request:**
```json
{
  "message": "Olá, teste do bot"
}
```

---

## 4. WhatsApp

### POST /whatsapp/connect
Iniciar conexão WhatsApp (gerar QR)

**Request:**
```json
{
  "botId": "507f1f77bcf86cd799439013"
}
```

**Response (200):**
```json
{
  "status": "waiting_qr",
  "qrCode": "data:image/png;base64,..."
}
```

---

### GET /whatsapp/status/{botId}
Status da conexão

**Response (200):**
```json
{
  "status": "connected",
  "phoneNumber": "+5511999999999",
  "connectedAt": "2026-05-31T12:00:00Z"
}
```

---

### DELETE /whatsapp/disconnect/{botId}
Desconectar WhatsApp

---

### POST /whatsapp/send-message
Enviar mensagem (não usar em produção - usar via automação)

**Request:**
```json
{
  "botId": "...",
  "to": "+5511999999999",
  "message": "Olá!",
  "mediaUrl": null
}
```

---

### GET /whatsapp/chats/{botId}
Listar chats do WhatsApp

---

## 5. Telegram

### POST /telegram/connect
Conectar bot Telegram

**Request:**
```json
{
  "botId": "...",
  "botToken": "123456:ABC-DEF..."
}
```

**Response (200):**
```json
{
  "status": "connected",
  "botUsername": "@meu_bot"
}
```

---

### DELETE /telegram/disconnect/{botId}
Desconectar Telegram

---

### POST /telegram/set-webhook
Configurar webhook

---

### GET /telegram/bot-info
Informações do bot conectado

---

## 6. Conversations

### GET /conversations
Listar conversas

**Query Params:**
- `botId`: filter by bot
- `status`: filter by status
- `page`: page number
- `limit`: items per page

**Response (200):**
```json
{
  "data": [
    {
      "id": "...",
      "customer": {
        "name": "Maria Santos",
        "phone": "+5511999999999"
      },
      "status": "active",
      "lastMessage": "Olá, gostaria de...",
      "lastMessageAt": "2026-05-31T12:00:00Z",
      "unreadCount": 2
    }
  ],
  "pagination": { ... }
}
```

---

### GET /conversations/{id}
Detalhes da conversa

---

### PUT /conversations/{id}/assign
Atribuir conversa a humano

**Request:**
```json
{
  "userId": "..."
}
```

---

### PUT /conversations/{id}/close
Fechar conversa

---

### PUT /conversations/{id}/reopen
Reabrir conversa

---

### DELETE /conversations/{id}
Deletar conversa (soft delete)

---

### GET /conversations/{id}/messages
Histórico de mensagens da conversa

---

## 7. Messages

### POST /messages
Enviar mensagem manual

**Request:**
```json
{
  "conversationId": "...",
  "content": "Olá, como posso ajudar?",
  "mediaUrl": null
}
```

---

### GET /messages/{id}
Detalhes da mensagem

---

### PUT /messages/{id}/read
Marcar como lida

---

### DELETE /messages/{id}
Deletar mensagem (soft delete)

---

## 8. Automation Rules

### GET /automations
Listar regras de automação

**Query Params:**
- `botId`: filter by bot
- `enabled`: filter by status

**Response (200):**
```json
{
  "data": [
    {
      "id": "...",
      "name": "Regra: Horário",
      "enabled": true,
      "priority": 10,
      "conditions": [...],
      "actions": [...]
    }
  ]
}
```

---

### POST /automations
Criar regra

**Request:**
```json
{
  "botId": "...",
  "name": "Regra de Saudação",
  "enabled": true,
  "priority": 10,
  "conditions": [
    {
      "type": "keyword",
      "field": "message.content",
      "operator": "contains",
      "value": "oi"
    }
  ],
  "actions": [
    {
      "type": "reply",
      "content": "Olá! Bem-vindo!",
      "delay": 0
    }
  ]
}
```

---

### PUT /automations/{id}
Atualizar regra

---

### DELETE /automations/{id}
Deletar regra

---

### PUT /automations/{id}/toggle
Ativar/desativar regra

---

### POST /automations/{id}/test
Testar regra

---

## 9. Analytics

### GET /analytics/summary
Resumo de estatísticas

**Query Params:**
- `botId`: filter by bot
- `startDate`: ISO date
- `endDate`: ISO date

**Response (200):**
```json
{
  "totalMessages": 1250,
  "totalConversations": 89,
  "avgResponseTime": 2.3,
  "messagesByProvider": {
    "whatsapp": 950,
    "telegram": 300
  },
  "conversationsByStatus": {
    "active": 45,
    "closed": 44
  }
}
```

---

### GET /analytics/timeline
Timeline de mensagens (para gráficos)

**Response (200):**
```json
{
  "data": [
    { "date": "2026-05-30", "count": 150 },
    { "date": "2026-05-31", "count": 200 }
  ]
}
```

---

### GET /analytics/top-contacts
Top contatos por volume

---

## 10. Admin

### GET /admin/users
Listar todos os usuários (admin only)

---

### PUT /admin/users/{id}/plan
Alterar plano do usuário

**Request:**
```json
{
  "planType": "pro",
  "expiresAt": "2026-12-31T23:59:59Z"
}
```

---

### PUT /admin/users/{id}/suspend
Suspender usuário

---

### GET /admin/metrics
Métricas globais da plataforma

**Response (200):**
```json
{
  "totalUsers": 1520,
  "activeUsers": 890,
  "totalBots": 2100,
  "totalMessages": 154000,
  "revenue": {
    "monthly": 45500,
    "yearly": 512000
  }
}
```

---

### GET /admin/logs
Logs de sistema

---

## 11. WebSocket

### WS /ws
WebSocket para eventos em tempo real

**Connection:**
```javascript
const ws = new WebSocket(`wss://api.autochat.pro/ws?token=${jwtToken}`);
```

**Events:**

```javascript
// Nova mensagem recebida
{
  "event": "message.new",
  "data": {
    "conversationId": "...",
    "message": {
      "id": "...",
      "role": "user",
      "content": "Olá!",
      "createdAt": "2026-05-31T12:00:00Z"
    }
  }
}

// Status do bot alterado
{
  "event": "bot.status_changed",
  "data": {
    "botId": "...",
    "status": "connected"
  }
}

// Nova conversa
{
  "event": "conversation.new",
  "data": {
    "id": "...",
    "customer": { ... }
  }
}

// Mensagem lida
{
  "event": "message.read",
  "data": {
    "messageId": "...",
    "readAt": "2026-05-31T12:00:05Z"
  }
}

// Typing indicator
{
  "event": "conversation.typing",
  "data": {
    "conversationId": "...",
    "isTyping": true
  }
}
```

---

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict (email já existe) |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## Rate Limiting

| Plano | Limit |
|-------|-------|
| Free | 100 req/min |
| Basic | 300 req/min |
| Pro | 1000 req/min |

Headers de resposta:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1685616000
```

---

## Erros

**Formato de erro:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  }
}
```

**Códigos de erro comuns:**
- `VALIDATION_ERROR`: Dados inválidos
- `AUTH_FAILED`: Credenciais inválidas
- `EMAIL_NOT_CONFIRMED`: Email não confirmado
- `PLAN_LIMIT_REACHED`: Limite do plano atingido
- `BOT_NOT_CONNECTED`: Bot não está conectado
- `LLM_ERROR`: Erro no serviço LLM
- `RATE_LIMIT_EXCEEDED`: Muitas requisições
