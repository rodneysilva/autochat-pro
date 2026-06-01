/**
 * Serviço de conversas.
 */

import { getHttpClient } from './http-client'

const CONVERSATIONS_PATH = '/conversations'
const DASHBOARD_PATH = '/dashboard'

export interface DashboardMetrics {
  bots: {
    total: number
    ativos: number
    pausados: number
  }
  mensagens: {
    total: number
  }
  conversas: {
    total: number
  }
  ia: {
    ativa: boolean
    bots_com_ia: number
  }
}

export interface ConversaCliente {
  id: string
  nome: string
  telefone: string | null
}

export interface Conversa {
  id: string
  bot_id: string
  cliente: ConversaCliente
  status: string
  ultima_mensagem_em: string | null
  criado_em: string
}

export interface ListaConversasResponse {
  data: Conversa[]
  total: number
  pagina: number
  tamanho_pagina: number
}

export const dashboardService = {
  async getMetrics(): Promise<DashboardMetrics> {
    const client = getHttpClient()
    return client.get<DashboardMetrics>(`${DASHBOARD_PATH}/metrics`)
  },
}

export const conversationsService = {
  async list(params?: {
    bot_id?: string
    status?: string
    pagina?: number
    tamanho_pagina?: number
  }): Promise<ListaConversasResponse> {
    const client = getHttpClient()
    const query = new URLSearchParams()
    if (params?.bot_id) query.set('bot_id', params.bot_id)
    if (params?.status) query.set('status_filter', params.status)
    if (params?.pagina) query.set('pagina', String(params.pagina))
    if (params?.tamanho_pagina) query.set('tamanho_pagina', String(params.tamanho_pagina))
    const qs = query.toString()
    return client.get<ListaConversasResponse>(`${CONVERSATIONS_PATH}${qs ? `?${qs}` : ''}`)
  },

  async getById(conversationId: string): Promise<Conversa> {
    const client = getHttpClient()
    return client.get<Conversa>(`${CONVERSATIONS_PATH}/${conversationId}`)
  },
}
