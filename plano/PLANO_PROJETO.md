# 📋 Plano de Desenvolvimento - AutoChat Pro

**Plataforma de Automação de Atendimento via WhatsApp e Telegram**

---

## 📊 Visão Geral

| Propriedade | Valor |
|-------------|-------|
| **Nome** | AutoChat Pro |
| **Tech Stack** | FastAPI, React, Vite, Tailwind, MongoDB, Redis |
| **LLM** | GLM-4.7-Flash (Z.AI, gratuito) |
| **WhatsApp** | Evolution API v2 |
| **Telegram** | Telegram Bot API (webhook direto) |
| **Deploy** | Docker Compose + Cloudflare Tunnel |
| **Público** | Pequenos negócios |
| **Progresso Atual** | 70% |

---

## 🌐 Arquitetura de Deploy

```
Internet
  │
  ▼
Cloudflare Tunnel (autochat.rodney.website)
  │
  ├── Frontend (nginx, :5174)
  │     ├── / → React SPA
  │     ├── /api/* → proxy backend
  │     └── /ws → proxy WebSocket
  │
  └── Docker Compose
        ├── backend (FastAPI, :8100)
        │     ├── /api/v1/telegram/webhook/{token}
        │     └── LLM GLM integration
        ├── mongodb (:27018)
        ├── redis (:6380)
        ├── evolution-api (WhatsApp, :8090)
        ├── evolution-db (PostgreSQL)
        └── postfix (SMTP)
```

### URLs
| Serviço | URL |
|---------|-----|
| Frontend | https://autochat.rodney.website |
| API | https://autochat.rodney.website/api/v1 |
| Webhook Telegram | https://autochat.rodney.website/api/v1/telegram/webhook/{token} |
| Evolution API | http://localhost:8090 |

---

## ✅ Progresso por Fase

- [x] **FASE 1: Fundação** - 100% completa
- [x] **FASE 2: Autenticação** - 100% completa
- [x] **FASE 3: Modelos de Dados** - 100% completa
- [x] **FASE 4: Integração WhatsApp** - 100% completa
- [x] **FASE 5: Integração Telegram** - 90% completa ✅ (falta deploy e testes E2E)
- [ ] **FASE 6: Automações** - 10% completa
- [x] **FASE 7: Integração LLM GLM** - 80% completa ✅
- [ ] **FASE 8: Chat Tempo Real** - 0% completa
- [ ] **FASE 9: Planos e Pagamentos** - 0% completa
- [ ] **FASE 10: Onboarding e Admin** - 0% completa

---

## 🎯 Definição do MVP (Minimum Viable Product)

Funcionalidades essenciais para o lançamento:

- [x] Autenticação com confirmação por email
- [x] Cadastro de bots WhatsApp e Telegram
- [x] Respostas automáticas configuráveis (automações)
- [x] Integração com LLM GLM para atendimento inteligente
- [x] Dashboard básico com estatísticas
- [x] Página de configurações do usuário (Perfil, Segurança, Notificações)
- [ ] Histórico de conversas (E2E)
- [ ] Chat em tempo real via WebSocket

---

## 📅 Cronograma por Fases

### FASE 1: Fundação (Semana 1-2) ✅ 100%
**Objetivo:** Estrutura base do projeto

#### Backend ✅
- [x] Setup do projeto FastAPI
- [x] Configuração MongoDB (docker-compose)
- [x] Configuração Redis para cache/filas
- [x] Estrutura de pastas e módulos (Clean Architecture / DDD)
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
- [x] Cliente HTTP configurado (Axios + nginx proxy)

#### DevOps ✅
- [x] Docker Compose completo
- [x] Setup de variáveis ambiente
- [x] Dockerfiles (backend + frontend + postfix)
- [x] Repositório Git + .gitignore
- [x] Nginx com proxy reverso para API
- [x] Cloudflare Tunnel (autochat.rodney.website)

---

### FASE 2: Autenticação (Semana 3) ✅ 100%
**Objetivo:** Sistema de usuários funcional

#### Backend ✅
- [x] Modelo User no MongoDB
- [x] Repositório MongoDB implementado
- [x] Registro de usuário
- [x] Login JWT (access + refresh tokens)
- [x] Confirmação por email (Postfix + templates HTML)
- [x] Confirmação por telefone
- [x] Recuperação de senha
- [x] Middleware de autenticação
- [x] Refresh token
- [x] Password hashing com argon2

#### Frontend ✅
- [x] Página de Login (dark mode, toggle senha)
- [x] Página de Cadastro
- [x] Confirmação de email/telefone
- [x] Recuperação de senha
- [x] Protected routes
- [x] Store de autenticação (Zustand + persist)
- [x] Página de Configurações (Perfil, Segurança, Notificações)

---

### FASE 3: Modelos de Dados Core (Semana 4) ✅ 100%
**Objetivo:** Estrutura de dados principal

#### Backend ✅
- [x] Modelo Plan (free, basic, pro)
- [x] Modelo Bot (whatsapp, telegram)
- [x] Modelo Conversation
- [x] Modelo Message
- [x] Modelo Analytics/Metrics
- [x] Relacionamentos e índices
- [x] Seeds de dados iniciais (planos + usuário teste)
- [x] Repositórios MongoDB implementados

#### Frontend ✅
- [x] Dashboard home
- [x] Navigation completa
- [x] Sidebar de navegação
- [x] Header com perfil usuário
- [x] HomePage com hero, features e planos

---

### FASE 4: Integração WhatsApp (Semana 5-6) ✅ 100%
**Objetivo:** Bots de WhatsApp funcionando

#### Backend ✅
- [x] Setup Evolution API
- [x] Geração de QR Code para conexão
- [x] Recebimento de mensagens
- [x] Envio de mensagens
- [x] Webhook system
- [x] Status de conexão
- [x] Conexão por telefone (pairing code)

#### Frontend ✅
- [x] Página "Adicionar Bot WhatsApp"
- [x] Display QR Code
- [x] Status de conexão
- [x] Formatação de número de telefone

---

### FASE 5: Integração Telegram (Semana 7) ✅ 90%
**Objetivo:** Bots de Telegram funcionando

#### Backend ✅
- [x] TelegramService (httpx, sem dependência python-telegram-bot)
- [x] Webhook endpoint `/api/v1/telegram/webhook/{bot_token}`
- [x] Recebimento de mensagens via webhook
- [x] Envio de mensagens via Telegram Bot API
- [x] Validação de bot token (getMe)
- [x] Setup/delete webhook endpoints
- [x] MessageProcessor adaptado para Telegram (LLM + automações)
- [ ] Testes E2E com bot real

#### Frontend ✅
- [x] AddBotPage com selector WhatsApp | Telegram
- [x] Input de Bot Token com validação
- [x] Auto-criação de bot Telegram + webhook setup
- [x] Telegram API service

#### Nota Técnica
- O Telegram **não é suportado pela Evolution API** (focada em WhatsApp)
- Integração feita diretamente com Telegram Bot API via webhook
- Bot token armazenado no MongoDB (`telegram_config.bot_token`)
- Webhook URL: `https://autochat.rodney.website/api/v1/telegram/webhook/{token}`

---

### FASE 6: Sistema de Automações (Semana 8) 🔄 10%
**Objetivo:** Configuração de respostas automáticas

#### Backend
- [x] Modelo AutomationRule
- [x] Avaliação de condições no MessageProcessor (WhatsApp + Telegram)
- [ ] Keyword matching avançado
- [ ] Respostas dinâmicas com variáveis
- [ ] Delay configurável na UI
- [ ] Fallback message

#### Frontend
- [ ] Editor de regras de automação
- [ ] Preview de regras
- [ ] Teste de regras

---

### FASE 7: Integração LLM GLM (Semana 9) ✅ 80%
**Objetivo:** Atendimento inteligente

#### Backend ✅
- [x] GLMService (OpenAI-compatible, httpx)
- [x] LLMService unificado (multi-provider: glm, openai, anthropic, ollama)
- [x] Prompt engineering base por bot
- [x] Contexto de conversa (ConversationContext)
- [x] Chat streaming via SSE
- [x] Chat completion (non-streaming)
- [x] Fallback para LLM legado
- [x] Modelo padrão: glm-4.7-flash (gratuito, 200K contexto)
- [ ] Fluxo de escolha de pedidos (catálogo)
- [ ] Fallback robusto para LLM offline

#### Frontend ✅
- [x] Configuração de prompt do bot (BotConfigPage)
- [x] Chat streaming endpoint
- [ ] Preview de chat com LLM E2E
- [ ] Configuração de catálogo/produtos

---

### FASE 8: Chat em Tempo Real (Semana 10)
**Objetivo:** Dashboard de conversas

#### Backend
- [x] WebSocket (FastAPI WebSockets)
- [x] Eventos de nova mensagem
- [ ] Histórico de conversas persistido
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
- [x] Página de planos (HomePage)
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

### Collections
- `users` — Usuários com plano e status
- `bots` — Bots WhatsApp/Telegram
- `conversations` — Conversas com clientes
- `messages` — Mensagens das conversas
- `analytics` — Métricas e estatísticas
- `automation_rules` — Regras de automação
- `plans_config` — Configuração dos planos
- `system_settings` — Configurações do sistema

---

## 🔧 Stack Técnica Detalhada

### Backend
| Componente | Tecnologia | Status |
|------------|------------|--------|
| API | FastAPI | ✅ |
| Database | Motor (async MongoDB) | ✅ |
| Auth | JWT + argon2 | ✅ |
| WhatsApp | Evolution API v2 | ✅ |
| Telegram | Telegram Bot API (httpx) | ✅ |
| Queue | Redis + ARQ | ✅ Config |
| Validation | Pydantic v2 | ✅ |
| LLM | GLM-4.7-Flash (Z.AI) | ✅ |
| Email | Postfix SMTP | ✅ |

### Frontend
| Componente | Tecnologia | Status |
|------------|------------|--------|
| Framework | React 18 + Vite | ✅ |
| Language | TypeScript | ✅ |
| Styling | Tailwind CSS + Dark Mode | ✅ |
| State | Zustand + persist | ✅ |
| Router | React Router v6 | ✅ |
| HTTP | Axios + nginx proxy | ✅ |

### Infraestrutura
| Componente | Tecnologia | Status |
|------------|------------|--------|
| Containerização | Docker Compose | ✅ |
| Tunnel | Cloudflare Tunnel | ✅ |
| Domínio | autochat.rodney.website | ✅ |
| Reverse Proxy | Nginx (no container frontend) | ✅ |

---

## 🔑 Credenciais de Teste

| Campo | Valor |
|-------|-------|
| **Email** | admin@autochat.com |
| **Senha** | Admin@123 |
| **Plano** | Pro |
| **Email confirmado** | Sim |

---

## 🐛 Bugs Corrigidos

### Sessão 01/06/2026
1. **bcrypt incompatível** — passlib 1.7.4 não suporta bcrypt 5.x
2. **Formato de erro inconsistente** — Padronizado para PT
3. **timedelta não importado** — Entidade Usuario
4. **CORS** — Liberado para qualquer origem em desenvolvimento
5. **TypeScript errors** — Corrigidos todos
6. **Seed de teste** — Adicionado usuário admin automaticamente
7. **Frontend API URL** — Mudado para URL relativa via nginx proxy

### Sessão 03/06/2026
8. **LLM modelo inválido** — `glm-4` não existe mais na Z.AI; atualizado para `glm-4.7-flash` (gratuito)
9. **Telegram integração** — Criado TelegramService, webhook endpoint, MessageProcessor adaptado
10. **AddBotPage** — Adicionado suporte a Telegram com selector de tipo
11. **SettingsPage** — Implementada com abas Perfil, Segurança, Notificações

---

## 🚀 Próximos Passos Prioritários

1. **Deploy Docker** — `docker compose up -d` e testes E2E
2. **Teste Telegram E2E** — Criar bot no @BotFather, integrar, enviar mensagens
3. **Sistema de Automações** (FASE 6) — Editor visual de regras
4. **Chat em Tempo Real** (FASE 8) — WebSocket + UI de conversas
5. **Planos e Pagamentos** (FASE 9) — Stripe/PagSeguro

---

## 📱 Checklist Interativo

Acesse o checklist interativo em [`checklist.html`](./checklist.html) para acompanhar o progresso em tempo real.
