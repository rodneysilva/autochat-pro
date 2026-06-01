/**
 * Serviço de integração com automações.
 */

import { getHttpClient } from './http-client'

const AUTOMATIONS_PATH = '/automations'

export interface CondicaoDTO {
  tipo: string
  campo: string
  operador: string
  valor: string
  negar: boolean
}

export interface AcaoDTO {
  tipo: string
  delay: number
  conteudo: string
  parametros: Record<string, unknown>
}

export interface RegraResponse {
  id: string
  bot_id: string
  nome: string
  descricao: string
  ativa: boolean
  prioridade: number
  condicoes: CondicaoDTO[]
  acoes: AcaoDTO[]
  cooldown: number
  max_execucoes: number | null
  limite_por_conversa: number
  estatisticas: {
    total_execucoes: number
    ultima_execucao_em: string | null
  }
  criado_em: string
  atualizado_em: string
}

export interface ListaRegrasResponse {
  data: RegraResponse[]
  total: number
}

export interface CriarRegraRequest {
  bot_id: string
  nome: string
  descricao?: string
  condicoes: CondicaoDTO[]
  acoes: AcaoDTO[]
  prioridade?: number
  cooldown_seconds?: number
  ativa?: boolean
}

export interface AtualizarRegraRequest {
  nome?: string
  descricao?: string
  condicoes?: CondicaoDTO[]
  acoes?: AcaoDTO[]
  prioridade?: number
  cooldown_seconds?: number
  ativa?: boolean
}

export const automationsService = {
  async list(botId: string, pagina = 1, tamanhoPagina = 20): Promise<ListaRegrasResponse> {
    const client = getHttpClient()
    return client.get<ListaRegrasResponse>(
      `${AUTOMATIONS_PATH}?bot_id=${botId}&pagina=${pagina}&tamanho_pagina=${tamanhoPagina}`
    )
  },

  async getById(ruleId: string): Promise<RegraResponse> {
    const client = getHttpClient()
    return client.get<RegraResponse>(`${AUTOMATIONS_PATH}/${ruleId}`)
  },

  async create(data: CriarRegraRequest): Promise<RegraResponse> {
    const client = getHttpClient()
    return client.post<RegraResponse>(AUTOMATIONS_PATH, data)
  },

  async update(ruleId: string, data: AtualizarRegraRequest): Promise<RegraResponse> {
    const client = getHttpClient()
    return client.put<RegraResponse>(`${AUTOMATIONS_PATH}/${ruleId}`, data)
  },

  async delete(ruleId: string): Promise<{ mensagem: string }> {
    const client = getHttpClient()
    return client.delete<{ mensagem: string }>(`${AUTOMATIONS_PATH}/${ruleId}`)
  },

  async toggle(ruleId: string): Promise<RegraResponse> {
    const client = getHttpClient()
    return client.post<RegraResponse>(`${AUTOMATIONS_PATH}/${ruleId}/toggle`)
  },
}
