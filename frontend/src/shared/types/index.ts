/**
 * Tipos compartilhados do frontend.
 *
 * Este arquivo contém todos os tipos TypeScript compartilhados
 * entre diferentes camadas da aplicação frontend.
 */

// ========================================
// Tipos de Domínio
// ========================================

export type TipoPlano = 'free' | 'basic' | 'pro'

export type StatusUsuario = 'active' | 'suspended' | 'deleted'

export type TipoBot = 'whatsapp' | 'telegram'

export type StatusBot = 'active' | 'paused' | 'disconnected' | 'error' | 'connecting'

export type StatusConversa = 'active' | 'waiting' | 'closed' | 'archived'

export type PapelMensagem = 'user' | 'bot' | 'human' | 'system'

export type TipoMensagem = 'text' | 'image' | 'video' | 'audio' | 'document' | 'sticker' | 'location' | 'contact'

export type StatusEntrega = 'pending' | 'sent' | 'delivered' | 'read' | 'failed'

// ========================================
// Entidades
// ========================================

export interface ConfiguracaoPlano {
  tipo: TipoPlano
  max_bots: number
  max_mensagens_por_mes: number
  max_contatos: number
  features: string[]
  expira_em: string | null
  trial_termina_em: string | null
  trial_utilizado: boolean
}

export interface Usuario {
  id: string
  email: string
  nome: string
  telefone: string | null
  email_confirmado: boolean
  telefone_confirmado: boolean
  avatar: string | null
  plano: ConfiguracaoPlano
  criado_em: string
  atualizado_em: string
}

export interface WorkingHours {
  ativado: boolean
  inicio: string
  fim: string
  timezone: string
  mensagem_fora_horario: string
}

export interface LLMConfig {
  ativado: boolean
  modelo: string
  provider: string
  temperatura: number
  max_tokens: number
  max_context_messages: number
  system_prompt: string
  fallback_para_llm: boolean
}

export interface CatalogoItem {
  id: string
  nome: string
  descricao: string
  preco: number
  categoria: string
  imagem_url: string | null
}

export interface Catalogo {
  ativado: boolean
  itens: CatalogoItem[]
}

export interface WhatsAppConfig {
  numero_telefone: string | null
  qr_code: string | null
  profile_picture_url: string | null
}

export interface TelegramConfig {
  bot_username: string | null
  webhook_url: string | null
}

export interface EstatisticasBot {
  total_mensagens: number
  total_conversas: number
  tempo_resposta_medio: number
  ultima_reset: string | null
}

export interface Bot {
  id: string
  usuario_id: string
  nome: string
  tipo: TipoBot
  status: StatusBot
  mensagem_boas_vindas: string
  mensagem_despedida: string
  mensagem_resposta_padrao: string
  working_hours: WorkingHours
  llm_config: LLMConfig
  catalogo: Catalogo
  whatsapp_config: WhatsAppConfig | null
  telegram_config: TelegramConfig | null
  estatisticas: EstatisticasBot
  ultimo_erro: string | null
  ultimo_conectado_em: string | null
  criado_em: string
  atualizado_em: string
}

export interface DadosCliente {
  id: string
  nome: string
  telefone: string | null
  metadata: Record<string, unknown>
}

export interface ContextoConversa {
  intent_atual: string | null
  produto_atual: string | null
  carrinho: Array<{ produto_id: string; quantidade: number }>
  ultima_acao: string | null
}

export interface Conversa {
  id: string
  bot_id: string
  usuario_atendente_id: string | null
  cliente: DadosCliente
  status: StatusConversa
  contexto: ContextoConversa
  primeira_mensagem_em: string | null
  ultima_mensagem_em: string | null
  ultima_atividade_em: string | null
  fechada_em: string | null
  criado_em: string
  atualizado_em: string
}

export interface MetadataMidia {
  mime_type: string | null
  tamanho: number | null
  duracao: number | null
  legenda: string | null
}

export interface Mensagem {
  id: string
  conversa_id: string
  papel: PapelMensagem
  conteudo: string
  tipo: TipoMensagem
  media_url: string | null
  media_metadata: MetadataMidia | null
  provedor: string
  provedor_mensagem_id: string | null
  status_entrega: StatusEntrega
  entregue_em: string | null
  lida_em: string | null
  criado_em: string
}

// ========================================
// DTOs de Requisição
// ========================================

export interface LoginRequest {
  email: string
  senha: string
}

export interface RegistroRequest {
  email: string
  senha: string
  nome: string
  telefone?: string
}

export interface CriarBotRequest {
  nome: string
  tipo: TipoBot
  mensagem_boas_vindas?: string
  mensagem_despedida?: string
}

export interface AtualizarBotRequest {
  nome?: string
  mensagem_boas_vindas?: string
  mensagem_despedida?: string
  mensagem_resposta_padrao?: string
}

export interface EnviarMensagemRequest {
  conversa_id: string
  conteudo: string
  media_url?: string
}

// ========================================
// DTOs de Resposta
// ========================================

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  usuario: Usuario
}

export interface ErrorResponse {
  erro: {
    codigo: string
    mensagem: string
    detalhes?: Record<string, unknown>
  }
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  pagina: number
  tamanho_pagina: number
}

// ========================================
// Tipos de WebSocket
// ========================================

export interface WebSocketEvent {
  event: string
  data: unknown
}

export interface MensagemNovaEvent {
  event: 'message.new'
  data: {
    conversa_id: string
    mensagem: Mensagem
  }
}

export interface BotStatusChangedEvent {
  event: 'bot.status_changed'
  data: {
    bot_id: string
    status: StatusBot
  }
}

export interface ConversaNovaEvent {
  event: 'conversation.new'
  data: {
    id: string
    cliente: DadosCliente
  }
}

export interface ConversaTypingEvent {
  event: 'conversation.typing'
  data: {
    conversa_id: string
    esta_digitando: boolean
  }
}

// ========================================
// Tipos de UI
// ========================================

export type Tema = 'light' | 'dark' | 'system'

export interface ToastData {
  id: string
  tipo: 'success' | 'error' | 'warning' | 'info'
  titulo: string
  mensagem: string
}

export interface MenuItem {
  id: string
  label: string
  icone: string
  caminho: string
  filhos?: MenuItem[]
}

export type ViewMode = 'grid' | 'list'
