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
| **Progresso Atual** | 60% |

---

## ✅ Progresso por Fase

- [x] **FASE 1: Fundação** - 100% completa
- [x] **FASE 2: Autenticação** - 100% completa ✅
- [x] **FASE 3: Modelos de Dados** - 100% completa ✅
- [x] **FASE 4: Integração WhatsApp** - 100% completa ✅
- [ ] **FASE 5: Integração Telegram** - 0% completa
- [ ] **FASE 6: Automações** - 10% completa
- [ ] **FASE 7: Integração LLM GLM** - 0% completa
- [ ] **FASE 8: Chat Tempo Real** - 0% completa
- [ ] **FASE 9: Planos e Pagamentos** - 0% completa
- [ ] **FASE 10: Onboarding e Admin** - 0% completa

---

## 🎯 Definição do MVP (Minimum Viable Product)

Funcionalidades essenciais para o lançamento:

- [x] Autenticação com confirmação por email
- [x] Cadastro de bots WhatsApp
- [ ] Respostas automáticas configuráveis
- [ ] Integração com LLM GLM para atendimento
- [x] Dashboard básico com estatísticas
- [ ] Histórico de conversas

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
- [x] Dockerfiles (backend + frontend)
- [x] Repositório Git + .gitignore
- [x] Nginx com proxy reverso para API

---

### FASE 2: Autenticação (Semana 3) ✅ 100%
**Objetivo:** Sistema de usuários funcional

#### Backend ✅
- [x] Modelo User no MongoDB (entidade criada)
- [x] Repositório MongoDB implementado
- [x] Registro de usuário
- [x] Login JWT (access + refresh tokens)
- [x] Confirmação por email (Postfix + templates HTML)
- [x] Confirmação por telefone
- [x] Recuperação de senha
- [x] Middleware de autenticação
- [x] Refresh token
- [x] Password hashing com bcrypt nativo

#### Frontend ✅
- [x] Página de Login (com dark mode e toggle de senha)
- [x] Página de Cadastro
- [x] Confirmação de email
- [x] Confirmação de telefone
- [x] Recuperação de senha
- [x] Protected routes
- [x] Store de autenticação (Zustand + persist)

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

#### Frontend
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
- [x] Página de planos (já no HomePage)
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
| Auth | JWT + bcrypt | ✅ |
| WhatsApp | Evolution API | ✅ |
| Telegram | python-telegram-bot | ⏳ |
| Queue | Redis + ARQ | ✅ Config |
| Validation | Pydantic v2 | ✅ |
| LLM | GLM (OpenAI-compatible) | ⏳ |

### Frontend
| Componente | Tecnologia | Status |
|------------|------------|--------|
| Framework | React 18 + Vite | ✅ |
| Language | TypeScript | ✅ |
| Styling | Tailwind CSS + Dark Mode | ✅ |
| State | Zustand + persist | ✅ |
| Router | React Router v6 | ✅ |
| HTTP | Axios + nginx proxy | ✅ |

---

## 🔑 Credenciais de Teste

| Campo | Valor |
|-------|-------|
| **Email** | admin@autochat.com |
| **Senha** | Admin@123 |
| **Plano** | Pro |
| **Email confirmado** | Sim |

---

## 🐛 Bugs Corrigidos (Sessão 01/06/2026)

1. **bcrypt incompatível** — passlib 1.7.4 não suporta bcrypt 5.x
2. **Formato de erro inconsistente** — Padronizado para PT `{erro: {codigo, mensagem}}`
3. **timedelta não importado** — Entidade Usuario
4. **CORS** — Liberado para qualquer origem em desenvolvimento
5. **TypeScript errors** — Corrigidos todos (AddBotPage, ConfirmPhonePage, etc.)
6. **Seed de teste** — Adicionado usuário admin automaticamente
7. **Frontend API URL** — Mudado para URL relativa via nginx proxy

---

## 🚀 Próximos Passos Prioritários

1. **Integração Telegram** (FASE 5)
2. **Sistema de Automações** (FASE 6)
3. **Integração LLM GLM** (FASE 7)
4. **Chat em Tempo Real** (FASE 8)

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
