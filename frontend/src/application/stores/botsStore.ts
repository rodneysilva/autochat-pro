import { create } from 'zustand'
import { botsService, type BotResponse } from '../../infrastructure/api/bots.service'

export type BotStatus = 'active' | 'paused' | 'disconnected' | 'error' | 'connecting'
export type BotType = 'whatsapp' | 'telegram'

export interface Bot {
  id: string
  usuario_id: string
  nome: string
  tipo: 'whatsapp' | 'telegram'
  status: BotStatus
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
    temperatura: number
    max_tokens: number
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

interface BotsState {
  bots: Bot[]
  selectedBot: Bot | null
  isLoading: boolean
  error: string | null
  setBots: (bots: Bot[]) => void
  setSelectedBot: (bot: Bot | null) => void
  addBot: (bot: Bot) => void
  updateBot: (id: string, updates: Partial<Bot>) => void
  removeBot: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  fetchBots: () => Promise<void>
}

// Mapeia resposta da API para o formato do store
function mapBotResponse(bot: BotResponse): Bot {
  return {
    id: bot.id,
    usuario_id: bot.usuario_id,
    nome: bot.nome,
    tipo: bot.tipo as BotType,
    status: bot.status,
    mensagem_boas_vindas: bot.mensagem_boas_vindas,
    mensagem_despedida: bot.mensagem_despedida,
    mensagem_resposta_padrao: bot.mensagem_resposta_padrao,
    working_hours: bot.working_hours,
    llm_config: bot.llm_config,
    estatisticas: bot.estatisticas,
    ultimo_erro: bot.ultimo_erro,
    ultimo_conectado_em: bot.ultimo_conectado_em,
    criado_em: bot.criado_em,
    atualizado_em: bot.atualizado_em,
  }
}

export const useBotsStore = create<BotsState>((set) => ({
  bots: [],
  selectedBot: null,
  isLoading: false,
  error: null,

  setBots: (bots) => set({ bots }),
  setSelectedBot: (bot) => set({ selectedBot: bot }),

  addBot: (bot) =>
    set((state) => ({ bots: [...state.bots, bot] })),

  updateBot: (id, updates) =>
    set((state) => ({
      bots: state.bots.map((bot) =>
        bot.id === id ? { ...bot, ...updates } : bot
      ),
      selectedBot:
        state.selectedBot?.id === id
          ? { ...state.selectedBot, ...updates }
          : state.selectedBot,
    })),

  removeBot: (id) =>
    set((state) => ({
      bots: state.bots.filter((bot) => bot.id !== id),
      selectedBot:
        state.selectedBot?.id === id ? null : state.selectedBot,
    })),

  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  fetchBots: async () => {
    set({ isLoading: true, error: null })
    try {
      const result = await botsService.list()
      set({ bots: result.data.map(mapBotResponse), isLoading: false })
    } catch (err: any) {
      const msg = err?.response?.data?.erro?.mensagem || 'Erro ao carregar bots'
      set({ error: msg, isLoading: false })
    }
  },
}))
