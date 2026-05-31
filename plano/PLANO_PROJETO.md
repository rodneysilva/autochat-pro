# 📋 Plano de Desenvolvimento - AutoChat Pro

**Plataforma de Automação de Atendimento via WhatsApp e Telegram**

---

## 📊 Visão Geral

| Propriedade | Valor |
|-------------|-------|
| **Nome** | AutoChat Pro |
| **Tech Stack** | FastAPI, React, Vite, Tailwind, MongoDB, Redis |
| **LLM** | GLM (on-premise) |
| **Público** | Pequenos negócios |
| **Prazo Estimado** | 10-12 semanas (1 dev) / 6-8 semanas (2 devs) |
| **Progresso Atual** | 50% |

---

## ✅ Progresso por Fase

- [x] **FASE 1: Fundação** - 100% completa
- [x] **FASE 2: Autenticação** - 100% completa ✅
- [ ] **FASE 3: Modelos de Dados** - 50% completa
- [ ] **FASE 4: Integração WhatsApp** - 0% completa
- [ ] **FASE 5: Integração Telegram** - 0% completa
- [ ] **FASE 6: Automações** - 10% completa
- [ ] **FASE 7: Integração LLM GLM** - 0% completa
- [ ] **FASE 8: Chat Tempo Real** - 0% completa
- [ ] **FASE 9: Planos e Pagamentos** - 0% completa
- [ ] **FASE 10: Onboarding e Admin** - 0% completa

---

## 🎯 Definição do MVP (Minimum Viable Product)

Funcionalidades essenciais para o lançamento:

- [ ] Autenticação com confirmação por email
- [ ] Cadastro de bots WhatsApp e Telegram
- [ ] Respostas automáticas configuráveis
- [ ] Integração com LLM GLM para atendimento
- [ ] Dashboard básico com estatísticas
- [ ] Histórico de conversas

---

## 📅 Cronograma por Fases

### FASE 1: Fundação (Semana 1-2) ✅ 100%
**Objetivo:** Estrutura base do projeto

#### Backend ✅
- [x] Setup do projeto FastAPI
- [x] Configuração MongoDB (docker-compose)
- [x] Configuração Redis para cache/filas
- [x] Estrutura de pastas e módulos (Clean Architecture)
- [x] Pydantic schemas base
- [x] Configuração variáveis ambiente (.env)
- [x] Setup de logging e monitoramento
- [x] Entidades do domínio (User, Bot, Conversation, AutomationRule)
- [x] Interfaces de repositórios
- [x] DTOs da aplicação
- [x] Exceções customizadas

#### Frontend ✅
- [x] Setup Vite + React + TypeScript
- [x] Configuração Tailwind CSS
- [x] Estrutura de rotas (React Router)
- [x] Layout base e componentes globais
- [x] Sistema de temas (dark/light)
- [x] Estado global (Zustand)
- [x] Tipos TypeScript
- [x] Cliente HTTP configurado

#### DevOps ✅
- [x] Docker Compose completo
- [x] Setup de variáveis ambiente
- [x] Dockerfiles (backend + frontend)
- [ ] Repositório Git + .gitignore

---

### FASE 2: Autenticação (Semana 3) ✅ 100%
**Objetivo:** Sistema de usuários funcional

#### Backend ✅
- [x] Modelo User no MongoDB (entidade criada)
- [x] Repositório MongoDB implementado
- [x] Registro de usuário
- [x] Login JWT
- [x] Confirmação por email (Postfix + templates HTML)
- [x] Confirmação por WhatsApp (sem SMS - custo zero)
- [x] Recuperação de senha
- [x] Middleware de autenticação
- [x] Refresh token

#### Frontend ✅
- [x] Página de Login
- [x] Página de Cadastro
- [x] Confirmação de email
- [x] Confirmação de telefone (WhatsApp)
- [x] Recuperação de senha
- [x] Protected routes
- [x] Context de autenticação (Zustand store)

---

### FASE 3: Modelos de Dados Core (Semana 4) ✅ 50%
**Objetivo:** Estrutura de dados principal

#### Backend ✅
- [x] Modelo Plan (free, basic, pro)
- [x] Modelo Bot (whatsapp, telegram)
- [x] Modelo Conversation
- [x] Modelo Message
- [ ] Modelo Analytics/Metrics
- [ ] Relacionamentos e índices
- [ ] Seeds de dados iniciais
- [ ] Repositórios MongoDB implementados

#### Frontend
- [ ] Dashboard home
- [ ] Navigation completa
- [ ] Sidebar de navegação
- [ ] Header com perfil usuário

---

### FASE 4: Integração WhatsApp (Semana 5-6)
**Objetivo:** Bots de WhatsApp funcionando

#### Backend
- [ ] Setup Baileys (WhatsApp open-source) ou Evolution API
- [ ] Geração de QR Code para conexão
- [ ] Recebimento de mensagens
- [ ] Envio de mensagens
- [ ] Webhook system
- [ ] Handler de desconexão
- [ ] Reconnection logic
- [ ] Upload de mídia

#### Frontend
- [ ] Página "Adicionar Bot WhatsApp"
- [ ] Display QR Code
- [ ] Status de conexão
- [ ] Teste de envio

---

### FASE 5: Integração Telegram (Semana 7)
**Objetivo:** Bots de Telegram funcionando

#### Backend
- [ ] Setup Telegram Bot API
- [ ] Webhook Telegram
- [ ] Recebimento de mensagens
- [ ] Envio de mensagens
- [ ] Comandos básicos (/start, /help)
- [ ] Inline buttons

#### Frontend
- [ ] Página "Adicionar Bot Telegram"
- [ ] Configuração de token
- [ ] Teste de envio

---

### FASE 6: Sistema de Automações (Semana 8) 🔄 10%
**Objetivo:** Configuração de respostas automáticas

#### Backend
- [x] Modelo AutomationRule
- [ ] Keyword matching
- [ ] Respostas dinâmicas
- [ ] Delay configurável
- [ ] Fallback message

#### Frontend
- [ ] Editor de regras de automação
- [ ] Preview de regras
- [ ] Teste de regras

---

### FASE 7: Integração LLM GLM (Semana 9)
**Objetivo:** Atendimento inteligente

#### Backend
- [ ] Cliente GLM (OpenAI-compatible API)
- [ ] Prompt engineering base
- [ ] Contexto de conversa
- [ ] Fluxo de escolha de pedidos
- [ ] Streaming de respostas
- [ ] Fallback para LLM

#### Frontend
- [ ] Configuração de prompt do bot
- [ ] Preview de chat com LLM
- [ ] Configuração de catálogo/produtos

---

### FASE 8: Chat em Tempo Real (Semana 10)
**Objetivo:** Dashboard de conversas

#### Backend
- [ ] WebSocket (FastAPI WebSockets)
- [ ] Eventos de nova mensagem
- [ ] Histórico de conversas
- [ ] Marcação de lida
- [ ] Transferência para humano

#### Frontend
- [ ] Interface de chat (lista + conversa)
- [ ] Input de mensagem
- [ ] Indicador de digitando
- [ ] Timeline de conversas
- [ ] Filtros e busca

---

### FASE 9: Planos e Pagamentos (Semana 11)
**Objetivo:** Sistema de assinaturas

#### Backend
- [ ] Limites por plano
- [ ] Upgrade/Downgrade
- [ ] Stripe/PagSeguro integration
- [ ] Webhooks de pagamento
- [ ] Trial period

#### Frontend
- [ ] Página de planos
- [ ] Checkout
- [ ] Gestão de assinatura
- [ ] Histórico de pagamentos

---

### FASE 10: Onboarding e Admin (Semana 12)
**Objetivo:** Experiência completa

#### Frontend
- [ ] Tour guiado first-login
- [ ] Tooltips e helps
- [ ] Modais de boas-vindas
- [ ] Checklist de configuração

#### Admin
- [ ] Dashboard administrativo
- [ ] Gestão de usuários
- [ ] Gestão de planos
- [ ] Métricas globais
- [ ] Logs de sistema

---

## 🗄️ Modelos de Dados (MongoDB)

### Collections Overview
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

### Collections

#### users
```javascript
{
  _id: ObjectId,
  email: String (unique),
  phone: String,
  emailConfirmed: Boolean,
  phoneConfirmed: Boolean,
  passwordHash: String,
  name: String,
  avatar: String,
  plan: {
    type: "free" | "basic" | "pro",
    maxBots: Number,
    maxMessagesPerMonth: Number,
    expiresAt: Date
  },
  status: "active" | "suspended" | "deleted",
  createdAt: Date,
  updatedAt: Date
}
```

#### bots
```javascript
{
  _id: ObjectId,
  userId: ObjectId (ref: users),
  name: String,
  type: "whatsapp" | "telegram",
  status: "active" | "paused" | "disconnected",
  config: {
    token: String,
    welcomeMessage: String,
    autoReplyEnabled: Boolean,
    llmEnabled: Boolean,
    llmPrompt: String
  },
  stats: {
    totalMessages: Number,
    totalConversations: Number
  },
  createdAt: Date
}
```

#### conversations
```javascript
{
  _id: ObjectId,
  botId: ObjectId (ref: bots),
  customer: {
    id: String,
    name: String,
    metadata: Object
  },
  status: "active" | "closed" | "archived",
  assignedTo: ObjectId (ref: users),
  lastMessageAt: Date,
  createdAt: Date
}
```

#### messages
```javascript
{
  _id: ObjectId,
  conversationId: ObjectId (ref: conversations),
  role: "user" | "bot" | "human",
  content: String,
  mediaType: "text" | "image" | "video",
  mediaUrl: String,
  metadata: Object,
  createdAt: Date
}
```

---

## 🔧 Stack Técnica Detalhada

### Backend
| Componente | Tecnologia | Status |
|------------|------------|--------|
| API | FastAPI | ✅ |
| ORM | Motor (async MongoDB) | ✅ Config |
| Auth | JWT + Passlib | ⏳ Implementar |
| WhatsApp | Evolution API | ⏳ |
| Telegram | python-telegram-bot | ⏳ |
| Queue | Redis + ARQ | ✅ Config |
| Validation | Pydantic v2 | ✅ |
| LLM | OpenAI-compatible | ⏳ |

### Frontend
| Componente | Tecnologia | Status |
|------------|------------|--------|
| Framework | React 18 + Vite | ✅ |
| Language | TypeScript | ✅ |
| Styling | Tailwind CSS | ✅ |
| State | Zustand | ⏳ |
| Router | React Router v6 | ⏳ |
| Forms | React Hook Form | ⏳ |
| Real-time | Socket.io | ⏳ |
| HTTP | Axios | ✅ |

---

## 🎉 Implementações Recentes

### ✅ Email SMTP (Postfix)
- Servidor Postfix Docker configurado
- Templates HTML para emails transacionais
- Suporte a DKIM/SPF
- Domínio: rodney.website
- Guia de configuração DNS em `/docs/CONFIGURACAO_DNS_EMAIL.md`

### ✅ Verificação via WhatsApp (Sem Custo)
- Substitui SMS por WhatsApp
- Usa Evolution API (integração futura)
- Custo: R$ 0
- Código de 6 dígitos enviado via mensagem

---

## 📝 Critérios de Sucesso

- [ ] Usuário consegue se cadastrar e confirmar email
- [ ] Usuário consegue conectar bot WhatsApp
- [ ] Usuário consegue conectar bot Telegram
- [ ] Bot responde automaticamente
- [ ] Bot usa LLM para atendimento
- [ ] Dashboard mostra conversas em tempo real
- [ ] Onboarding é claro e intuitivo

---

## 🚀 Próximos Passos Prioritários

1. **Implementar repositórios MongoDB** (Infrastructure layer)
2. **Criar caso de uso de autenticação** (Register, Login)
3. **Implementar endpoints de auth** (API layer)
4. **Criar páginas de login/cadastro** (Frontend)
5. **Integrar WhatsApp** (Evolution API)

---

## 📱 Checklist Interativo

Acesse o checklist interativo em [`checklist.html`](./checklist.html) para acompanhar o progresso em tempo real.

**Funcionalidades:**
- ✅ Design mobile-first responsivo
- ✅ Sidebar colapsável em mobile
- ✅ Filtros rápidos (todos/pendentes/concluídos)
- ✅ Salva progresso automaticamente
- ✅ Scroll suave entre seções
- ✅ Footer com estatísticas (mobile)
