/**
 * Serviço de integração com bots.
 *
 * Comunica com a API de bots para gerenciar bots do usuário.
 */

import { getHttpClient } from './http-client'

const BOTS_PATH = '/bots'

export interface BotResponse {
  id: string
  usuario_id: string
  nome: string
  tipo: string
  status: 'active' | 'paused' | 'disconnected' | 'error' | 'connecting'
  mensagem_boas_vindas: string
  mensagem_despedida: string
  mensagem_resposta_padrao: string
  working_hours: {
    ativado: boolean
    inicio: string
    fim: string
    timezone: string
    mensagem_fora_horario: string
  }
  llm_config: {
    ativado: boolean
    modelo: string
    provider: string
    temperatura: number
    max_tokens: number
    max_context_messages: number
    system_prompt: string
    fallback_para_llm: boolean
  }
  estatisticas: {
    total_mensagens: number
    total_conversas: number
    tempo_resposta_medio: number
  }
  ultimo_erro: string | null
  ultimo_conectado_em: string | null
  criado_em: string
  atualizado_em: string
}

export interface ListaBotsResponse {
  data: BotResponse[]
  total: number
  pagina: number
  tamanho_pagina: number
}

export const botsService = {
  /**
   * Cria um novo bot.
   */
  async create(data: { nome: string; tipo: string }): Promise<BotResponse> {
    const client = getHttpClient()
    return client.post<BotResponse>(BOTS_PATH, data)
  },

  /**
   * Lista bots do usuário.
   */
  async list(pagina = 1, tamanhoPagina = 20): Promise<ListaBotsResponse> {
    const client = getHttpClient()
    return client.get<ListaBotsResponse>(`${BOTS_PATH}?pagina=${pagina}&tamanho_pagina=${tamanhoPagina}`)
  },

  /**
   * Busca bot por ID.
   */
  async getById(botId: string): Promise<BotResponse> {
    const client = getHttpClient()
    return client.get<BotResponse>(`${BOTS_PATH}/${botId}`)
  },

  /**
   * Atualiza configuração do bot.
   */
  async update(botId: string, data: Partial<BotResponse>): Promise<BotResponse> {
    const client = getHttpClient()
    return client.put<BotResponse>(`${BOTS_PATH}/${botId}`, data)
  },

  /**
   * Deleta um bot.
   */
  async delete(botId: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.delete<{ message: string }>(`${BOTS_PATH}/${botId}`)
  },

  /**
   * Pausa um bot.
   */
  async pause(botId: string): Promise<BotResponse> {
    const client = getHttpClient()
    return client.post<BotResponse>(`${BOTS_PATH}/${botId}/pause`)
  },

  /**
   * Retoma um bot pausado.
   */
  async resume(botId: string): Promise<BotResponse> {
    const client = getHttpClient()
    return client.post<BotResponse>(`${BOTS_PATH}/${botId}/resume`)
  },
}
