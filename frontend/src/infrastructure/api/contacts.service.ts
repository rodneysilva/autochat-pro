/**
 * Serviço de contatos.
 */

import { getHttpClient } from './http-client'

const CONTACTS_PATH = '/contacts'

export interface Contato {
  id: string
  bot_id: string
  nome: string
  telefone: string
  email: string | null
  origem: string
  tags: string[]
  status: string
  ultima_mensagem_em: string | null
  total_mensagens: number
  total_conversas: number
  criado_em: string
}

export interface ListaContatosResponse {
  data: Contato[]
  total: number
  pagina: number
  tamanho_pagina: number
}

export const contactsService = {
  async list(params?: {
    bot_id?: string
    tag?: string
    search?: string
    pagina?: number
    tamanho_pagina?: number
  }): Promise<ListaContatosResponse> {
    const client = getHttpClient()
    const query = new URLSearchParams()
    if (params?.bot_id) query.set('bot_id', params.bot_id)
    if (params?.tag) query.set('tag', params.tag)
    if (params?.search) query.set('search', params.search)
    if (params?.pagina) query.set('pagina', String(params.pagina))
    if (params?.tamanho_pagina) query.set('tamanho_pagina', String(params.tamanho_pagina))
    const qs = query.toString()
    return client.get<ListaContatosResponse>(`${CONTACTS_PATH}${qs ? `?${qs}` : ''}`)
  },

  async delete(contactId: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.delete<{ message: string }>(`${CONTACTS_PATH}/${contactId}`)
  },
}
