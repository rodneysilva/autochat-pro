import { getHttpClient } from './http-client'

export interface BusinessTemplate {
  key: string
  nome: string
  icon: string
  descricao: string
}

export interface TemplateDetail {
  key: string
  nome: string
  icon: string
  descricao: string
  campos_extras: { chave: string; label: string; placeholder: string }[]
  horario_padrao: { ativado: boolean; inicio: string; fim: string; timezone: string }
}

const api = getHttpClient()

export const templateService = {
  listTemplates: async (): Promise<BusinessTemplate[]> => {
    const response: any = await api.get('/bots/templates')
    return response.templates
  },

  getTemplate: async (key: string): Promise<TemplateDetail> => {
    return await api.get<TemplateDetail>(`/bots/templates/${key}`)
  },

  applyToBot: async (templateKey: string, botId: string, campos: Record<string, string> = {}): Promise<any> => {
    return await api.post(`/bots/templates/${templateKey}/apply?bot_id=${botId}`, campos)
  },
}
