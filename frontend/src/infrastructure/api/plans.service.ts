/**
 * Serviço de planos.
 */

import { getHttpClient } from './http-client'

const PLANS_PATH = '/plans'

export interface PlanConfig {
  tipo: string
  max_bots: number
  max_messages_per_month: number
  max_contacts: number
  max_automation_rules: number
  max_conversations: number
  features: string[]
}

export interface PlansResponse {
  plans: PlanConfig[]
}

export interface CurrentPlanResponse {
  tipo: string
  max_bots: number
  max_mensagens_por_mes: number
  max_contatos: number
  features: string[]
  expira_em: string | null
  trial_termina_em: string | null
  trial_utilizado: boolean
  usage: {
    bots: number
    contacts: number
  }
}

export const plansService = {
  async list(): Promise<PlansResponse> {
    const client = getHttpClient()
    return client.get<PlansResponse>(PLANS_PATH)
  },

  async getCurrent(): Promise<CurrentPlanResponse> {
    const client = getHttpClient()
    return client.get<CurrentPlanResponse>(`${PLANS_PATH}/current`)
  },

  async upgrade(planType: string): Promise<{ message: string; plan: any }> {
    const client = getHttpClient()
    return client.post<{ message: string; plan: any }>(`${PLANS_PATH}/upgrade?plan_type=${planType}`)
  },
}
