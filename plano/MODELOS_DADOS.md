# 🗄️ Modelos de Dados - AutoChat Pro

**Estrutura completa do MongoDB Schema**

---

## Collections Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE STRUCTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │    users     │◄────►│     bots     │◄────►│conversations │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│         │                      │                      │         │
│         ▼                      ▼                      ▼         │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │    plans     │      │  automation_ │      │   messages   │ │
│  │              │      │    rules     │◄────►│              │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│                                                      │         │
│                                                      ▼         │
│                                              ┌──────────────┐ │
│                                              │    metrics   │ │
│                                              └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Collection: `users`

**Propósito:** Armazenar informações dos usuários da plataforma

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  
  // Identificação
  email: "usuario@exemplo.com",
  emailConfirmed: false,
  emailConfirmedAt: ISODate("2026-05-31T12:00:00Z"),
  phone: "+5511999999999",
  phoneConfirmed: false,
  phoneConfirmedAt: null,
  
  // Autenticação
  passwordHash: "$2b$12$...", // bcrypt
  lastLoginAt: ISODate("2026-05-31T12:00:00Z"),
  
  // Perfil
  name: "João Silva",
  avatar: null, // URL ou null
  
  // Plano
  plan: {
    type: "free", // "free" | "basic" | "pro"
    maxBots: 1,
    maxMessagesPerMonth: 100,
    maxContacts: 50,
    features: ["basic_automation", "limited_llm"],
    expiresAt: null, // para planos pagos
    trialEndsAt: ISODate("2026-06-30T23:59:59Z"),
    trialUsed: false
  },
  
  // Status
  status: "active", // "active" | "suspended" | "deleted"
  
  // Timestamps
  createdAt: ISODate("2026-05-31T10:00:00Z"),
  updatedAt: ISODate("2026-05-31T12:00:00Z"),
  deletedAt: null
}
```

### Índices
```javascript
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ phone: 1 }, { unique: true, sparse: true })
db.users.createIndex({ status: 1, createdAt: -1 })
db.users.createIndex({ "plan.type": 1 })
```

---

## 2. Collection: `plans`

**Propósito:** Configurações dos planos disponíveis

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439012"),
  
  // Identificação
  name: "basic", // "free" | "basic" | "pro"
  displayName: "Plano Básico",
  description: "Para pequenos negócios",
  
  // Limites
  limits: {
    maxBots: 3,
    maxMessagesPerMonth: 5000,
    maxContacts: 500,
    maxAutomationRules: 10,
    maxConversations: 100
  },
  
  // Features
  features: {
    whatsapp: true,
    telegram: true,
    llm: true,
    advancedAnalytics: false,
    apiAccess: false,
    prioritySupport: false,
    customDomain: false
  },
  
  // Preços (BRL)
  pricing: {
    monthly: 49.90,
    yearly: 499.00, // ~17% desconto
    trialDays: 14
  },
  
  // Stripe/Payment
  stripePriceId: "price_basic_monthly",
  
  // Status
  active: true,
  
  // Timestamps
  createdAt: ISODate("2026-01-01T00:00:00Z"),
  updatedAt: ISODate("2026-05-31T10:00:00Z")
}
```

---

## 3. Collection: `bots`

**Propósito:** Configuração dos bots de cada usuário

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439013"),
  
  // Relacionamento
  userId: ObjectId("507f1f77bcf86cd799439011"),
  
  // Identificação
  name: "Bot de Atendimento - Loja X",
  type: "whatsapp", // "whatsapp" | "telegram"
  
  // Status
  status: "active", // "active" | "paused" | "disconnected" | "error"
  lastError: null,
  lastConnectedAt: ISODate("2026-05-31T12:00:00Z"),
  
  // Configuração por tipo
  whatsappConfig: {
    session: null, // Dados da sessão Baileys
    phoneNumber: null, // Número conectado
    qrCode: null, // QR Code para conexão
    businessProfile: null
  },
  
  telegramConfig: {
    botToken: "123456:ABC-DEF...",
    botUsername: "loja_x_bot",
    webhookUrl: "https://api.autochat.pro/webhooks/telegram/bot_id"
  },
  
  // Configurações Gerais
  settings: {
    welcomeMessage: "Olá! Sou o assistente virtual da Loja X. Como posso ajudar?",
    goodbyeMessage: "Obrigado pelo contato!",
    defaultResponse: "Desculpe, não entendi. Pode reformular?",
    workingHours: {
      enabled: false,
      start: "09:00",
      end: "18:00",
      timezone: "America/Sao_Paulo",
      outsideHoursMessage: "Estamos fora do horário. Retornarei em breve."
    }
  },
  
  // LLM
  llmConfig: {
    enabled: true,
    model: "glm-4",
    temperature: 0.7,
    maxTokens: 500,
    systemPrompt: "Você é um assistente de atendimento...",
    fallbackToLLM: true // Usa LLM se nenhuma regra bater
  },
  
  // Catálogo (para escolha de pedidos)
  catalog: {
    enabled: true,
    items: [
      {
        id: "item_1",
        name: "Produto X",
        description: "Descrição do produto",
        price: 99.90,
        category: "Categoria A",
        imageUrl: null
      }
    ]
  },
  
  // Estatísticas (cache)
  stats: {
    totalMessages: 1250,
    totalConversations: 89,
    avgResponseTime: 2.3, // segundos
    lastResetAt: ISODate("2026-05-01T00:00:00Z")
  },
  
  // Timestamps
  createdAt: ISODate("2026-05-31T10:00:00Z"),
  updatedAt: ISODate("2026-05-31T12:00:00Z")
}
```

### Índices
```javascript
db.bots.createIndex({ userId: 1, type: 1 })
db.bots.createIndex({ status: 1 })
db.bots.createIndex({ type: 1, status: 1 })
```

---

## 4. Collection: `automation_rules`

**Propósito:** Regras de automação para respostas automáticas

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439014"),
  
  // Relacionamento
  botId: ObjectId("507f1f77bcf86cd799439013"),
  
  // Identificação
  name: "Regra: Horário de Funcionamento",
  description: "Informa horário quando cliente perguntar",
  enabled: true,
  priority: 10, // 1-100, maior = maior prioridade
  
  // Condições (OR entre itens do array)
  conditions: [
    {
      type: "keyword", // "keyword" | "regex" | "time" | "intent"
      field: "message.content",
      operator: "contains", // "contains" | "equals" | "starts_with" | "regex"
      value: "horário"
    }
  ],
  
  // Ações (executadas em sequência)
  actions: [
    {
      type: "reply", // "reply" | "forward" | "llm" | "tag" | "close"
      delay: 0, // segundos antes de executar
      content: "Nosso horário é de segunda a sexta, 9h às 18h"
    }
  ],
  
  // Configurações adicionais
  cooldown: 300, // segundos antes de executar novamente para mesma conversa
  maxExecutions: null, // null = ilimitado
  limitPerConversation: 1,
  
  // Estatísticas
  stats: {
    totalExecutions: 450,
    lastExecutedAt: ISODate("2026-05-31T11:30:00Z")
  },
  
  // Timestamps
  createdAt: ISODate("2026-05-31T10:00:00Z"),
  updatedAt: ISODate("2026-05-31T11:30:00Z")
}
```

---

## 5. Collection: `conversations`

**Propósito:** Histórico de conversas com clientes

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439015"),
  
  // Relacionamentos
  botId: ObjectId("507f1f77bcf86cd799439013"),
  assignedTo: ObjectId("507f1f77bcf86cd799439011"), // null ou userId (humano)
  
  // Cliente
  customer: {
    id: "5511999999999", // phone ou telegram_id
    name: "Maria Santos",
    phone: "+5511999999999",
    telegramId: null,
    metadata: {
      source: "whatsapp",
      country: "BR",
      tags: ["cliente_frequente", "vip"]
    }
  },
  
  // Status
  status: "active", // "active" | "waiting" | "closed" | "archived"
  
  // Contexto da conversa (para LLM)
  context: {
    currentIntent: "pedido",
    currentProduct: null,
    cart: [],
    lastAction: "asked_about_product"
  },
  
  // Timestamps importantes
  firstMessageAt: ISODate("2026-05-31T10:00:00Z"),
  lastMessageAt: ISODate("2026-05-31T12:00:00Z"),
  lastActivityAt: ISODate("2026-05-31T12:00:00Z"),
  closedAt: null,
  
  // Timestamps
  createdAt: ISODate("2026-05-31T10:00:00Z"),
  updatedAt: ISODate("2026-05-31T12:00:00Z")
}
```

### Índices
```javascript
db.conversations.createIndex({ botId: 1, status: 1 })
db.conversations.createIndex({ "customer.id": 1 })
db.conversations.createIndex({ lastMessageAt: -1 })
db.conversations.createIndex({ status: 1, lastActivityAt: -1 })
```

---

## 6. Collection: `messages`

**Propósito:** Mensagens individuais das conversas

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439016"),
  
  // Relacionamento
  conversationId: ObjectId("507f1f77bcf86cd799439015"),
  
  // Tipo
  role: "user", // "user" | "bot" | "human" | "system"
  
  // Conteúdo
  content: "Olá, gostaria de saber o preço do produto X",
  
  // Mídia
  mediaType: "text", // "text" | "image" | "video" | "audio" | "document" | "sticker"
  mediaUrl: null,
  mediaMetadata: {
    mimeType: null,
    size: null,
    duration: null, // para audio/video
    caption: null
  },
  
  // Metadados da mensagem original
  provider: "whatsapp", // "whatsapp" | "telegram"
  providerMessageId: "wa_id_123456",
  
  // Status de envio
  deliveryStatus: "delivered", // "pending" | "sent" | "delivered" | "read" | "failed"
  deliveredAt: ISODate("2026-05-31T12:00:05Z"),
  readAt: ISODate("2026-05-31T12:00:10Z"),
  
  // Se gerado por LLM
  llmMetadata: {
    model: "glm-4",
    promptTokens: 50,
    completionTokens: 30,
    totalTokens: 80
  },
  
  // Se gerado por regra
  automationRuleId: null,
  
  // Timestamp
  createdAt: ISODate("2026-05-31T12:00:00Z")
}
```

### Índices
```javascript
db.messages.createIndex({ conversationId: 1, createdAt: 1 })
db.messages.createIndex({ providerMessageId: 1 })
db.messages.createIndex({ createdAt: -1 })
```

---

## 7. Collection: `analytics_events`

**Propósito:** Eventos para analytics e métricas

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439017"),
  
  // Relacionamento
  userId: ObjectId("507f1f77bcf86cd799439011"),
  botId: ObjectId("507f1f77bcf86cd799439013"),
  conversationId: ObjectId("507f1f77bcf86cd799439015"),
  
  // Evento
  eventType: "message_sent", // "message_sent" | "message_received" | "conversation_started" | "llm_used" | "automation_triggered"
  
  // Dados do evento
  eventData: {
    provider: "whatsapp",
    automationRuleId: null,
    llmModel: "glm-4",
    responseTime: 1.5
  },
  
  // Para agregações
  date: ISODate("2026-05-31T00:00:00Z"), // para índice
  
  // Timestamp
  createdAt: ISODate("2026-05-31T12:00:00Z")
}
```

---

## 8. Collection: `verification_codes`

**Propósito:** Códigos de verificação (email/SMS)

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439018"),
  
  // Identificação
  type: "email_confirmation", // "email_confirmation" | "phone_confirmation" | "password_reset"
  identifier: "usuario@exemplo.com", // email ou phone
  
  // Código
  code: "123456",
  expiresAt: ISODate("2026-05-31T13:00:00Z"),
  
  // Status
  used: false,
  usedAt: null,
  attempts: 0,
  
  // Timestamp
  createdAt: ISODate("2026-05-31T12:00:00Z")
}
```

### Índices
```javascript
db.verification_codes.createIndex({ identifier: 1, type: 1, expiresAt: 1 })
db.verification_codes.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 })
```

---

## Relacionamentos

```
users (1) ─────< (N) bots
 │                    │
 │                    │
 │                 automation_rules (botId)
 │                    │
 │                    ▼
 │                 conversations (botId) ──> messages (conversationId)
 │                    │
 │                    ▼
 │                 analytics_events (botId, userId, conversationId)
 │
 └──> plans (plan.type)
```

---

## Estratégias de Query Comuns

### 1. Buscar conversas recentes de um bot
```javascript
db.conversations.find({ 
  botId: ObjectId("..."), 
  status: "active" 
}).sort({ lastMessageAt: -1 }).limit(20)
```

### 2. Buscar mensagens de uma conversa
```javascript
db.messages.find({ 
  conversationId: ObjectId("...") 
}).sort({ createdAt: 1 })
```

### 3. Estatísticas diárias de um bot
```javascript
db.analytics_events.aggregate([
  { $match: { botId: ObjectId("..."), date: { $gte: ISODate("...") } } },
  { $group: { 
    _id: "$eventType", 
    count: { $sum: 1 } 
  }}
])
```

### 4. Verificar limites do plano do usuário
```javascript
db.users.aggregate([
  { $match: { _id: ObjectId("...") } },
  { $lookup: { 
    from: "bots", 
    localField: "_id", 
    foreignField: "userId", 
    as: "bots" 
  }},
  { $project: {
    plan: 1,
    botCount: { $size: "$bots" }
  }}
])
```

---

## Considerações de Performance

1. **TTL Index**: `verification_codes` tem auto-expiração
2. **Sharding**: Considerar shard por `userId` para multi-tenant
3. **Caching**: Usar Redis para sessões e dados frequentemente acessados
4. **Archive**: Mensagens antigas (>90 dias) podem ser arquivadas
5. **Analytics**: Considerar TimescaleDB ou similar para analytics pesados
