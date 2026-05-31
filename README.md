# 🤖 AutoChat Pro

Plataforma de automação de atendimento via WhatsApp e Telegram para pequenos negócios.

## 📋 Sobre o Projeto

AutoChat Pro é uma solução completa que permite pequenos negócios automatizarem seu atendimento via WhatsApp e Telegram, com suporte a:

- ✅ Múltiplos bots por usuário (conforme plano)
- ✅ Automação de respostas
- ✅ Integração com LLM GLM para atendimento inteligente
- ✅ Dashboard em tempo real
- ✅ Gestão de conversas
- ✅ Catálogo de produtos

## 🏗️ Arquitetura

O projeto segue **Clean Architecture**, **SOLID** e **DDD** (Domain-Driven Design):

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION (API/UI)                     │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │   FastAPI (BE)   │         │    React (FE)     │        │
│  └──────────────────┘         └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                          │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │   Use Cases      │         │      DTOs         │        │
│  └──────────────────┘         └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │    Entities      │         │  Repository I/F   │        │
│  └──────────────────┘         └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐│
│  │   MongoDB        │  │     Redis         │  │   LLM     ││
│  └──────────────────┘  └──────────────────┘  └───────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Linguagem**: Python 3.11+
- **Banco de Dados**: MongoDB
- **Cache/Filas**: Redis
- **LLM**: GLM (OpenAI-compatible)

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Estilização**: Tailwind CSS
- **Gerenciamento de Estado**: Zustand
- **HTTP**: Axios
- **WebSocket**: Socket.io

## 📁 Estrutura do Projeto

```
autochat-pro/
├── backend/
│   ├── src/
│   │   ├── domain/              # Camada de Domínio
│   │   │   ├── entities/        # Entidades do domínio
│   │   │   ├── repositories/    # Interfaces de repositórios
│   │   │   └── services/        # Serviços de domínio
│   │   ├── application/         # Camada de Aplicação
│   │   │   ├── use_cases/       # Casos de uso
│   │   │   ├── dto/             # Data Transfer Objects
│   │   │   └── services/        # Serviços de aplicação
│   │   ├── infrastructure/      # Camada de Infraestrutura
│   │   │   ├── database/        # Implementação MongoDB
│   │   │   ├── repositories/    # Repositórios concretos
│   │   │   ├── external_services/ # APIs externas
│   │   │   └── cache/           # Redis
│   │   ├── api/                 # Camada de Apresentação
│   │   │   ├── v1/endpoints/    # Endpoints da API
│   │   │   ├── middleware/      # Middlewares
│   │   │   └── dependencies/    # Injeção de dependências
│   │   ├── shared/              # Utilidades compartilhadas
│   │   │   ├── exceptions/      # Exceções customizadas
│   │   │   ├── validators/      # Validadores
│   │   │   └── utils/           # Funções auxiliares
│   │   └── main.py              # Entry point
│   ├── tests/                   # Testes
│   ├── requirements.txt          # Dependências Python
│   ├── Dockerfile              # Docker do backend
│   └── .env                    # Variáveis de ambiente
│
├── frontend/
│   ├── src/
│   │   ├── domain/              # Tipos de domínio
│   │   ├── application/         # Casos de uso e hooks
│   │   ├── infrastructure/      # Cliente HTTP e WebSocket
│   │   ├── presentation/        # Componentes UI
│   │   │   ├── pages/          # Páginas
│   │   │   ├── components/     # Componentes reutilizáveis
│   │   │   └── layouts/        # Layouts
│   │   └── shared/              # Utilidades compartilhadas
│   │       ├── types/          # Tipos TypeScript
│   │       ├── helpers/        # Funções auxiliares
│   │       └── constants/      # Constantes
│   ├── public/                  # Arquivos estáticos
│   ├── package.json            # Dependências Node
│   ├── vite.config.ts          # Config Vite
│   ├── tailwind.config.ts      # Config Tailwind
│   └── Dockerfile              # Docker do frontend
│
├── plano/                      # Documentação do projeto
│   ├── PLANO_PROJETO.md        # Plano detalhado
│   ├── MODELOS_DADOS.md        # Modelos de dados
│   ├── API_ENDPOINTS.md         # Documentação da API
│   └── checklist.html          # Checklist interativo
│
└── docker-compose.yml          # Orquestração dos serviços
```

## 🚀 Como Executar

### Pré-requisitos

- Docker e Docker Compose
- Node.js 20+ (para desenvolvimento local do frontend)
- Python 3.11+ (para desenvolvimento local do backend)

### Com Docker

```bash
# Clonar repositório
git clone <repositorio>
cd autochat-pro

# Copiar arquivo de ambiente
cp backend/.env.example backend/.env

# Iniciar todos os serviços
docker-compose up -d

# Acompanhar logs
docker-compose logs -f
```

Acesse:
- 🌐 Frontend: http://localhost:5173
- 📚 API Docs: http://localhost:8000/docs
- 🐘 MongoDB: mongodb://localhost:27017
- 🔴 Redis: redis://localhost:6379

### Desenvolvimento Local

#### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar
uvicorn src.main:app --reload
```

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Executar
npm run dev
```

## 📝 Princípios de Código

### Clean Architecture

- **Independência de frameworks**: O domínio não depende de frameworks externos
- **Testabilidade**: O código é facilmente testável
- **Independência de UI**: A lógica de negócio não conhece a UI
- **Independência de banco**: O domínio não sabe qual banco é usado
- **Independência de agentes externos**: O domínio não conhece APIs externas

### SOLID

- **S**ingle Responsibility: Cada classe tem uma única responsabilidade
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Subtipos são substituíveis
- **I**nterface Segregation: Interfaces específicas para clientes
- **D**ependency Inversion: Dependir de abstrações, não de implementações

### DDD

- **Entidades**: Objetos com identidade única e lógica de negócio
- **Value Objects**: Objetos sem identidade, imutáveis
- **Aggregates**: Coleções de objetos tratadas como uma unidade
- **Repositories**: Interfaces para acesso a dados
- **Domain Services**: Lógica de negócio que não pertence a entidades
- **Use Cases**: Aplicação de casos de uso do domínio

## 📄 Licença

Este projeto é proprietário. Todos os direitos reservados.

## 👥 Time

Desenvolvido com ❤️ usando Clean Architecture, SOLID e DDD.
