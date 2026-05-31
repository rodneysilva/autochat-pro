import { create } from 'zustand'

export type BotType = 'whatsapp' | 'telegram'
export type BotStatus = 'active' | 'paused' | 'disconnected' | 'connecting'

export interface Bot {
  id: string
  userId: string
  name: string
  type: BotType
  status: BotStatus
  config: {
    token?: string
    welcomeMessage: string
    autoReplyEnabled: boolean
    llmEnabled: boolean
    llmPrompt?: string
  }
  stats: {
    totalMessages: number
    totalConversations: number
  }
  createdAt: Date
  updatedAt: Date
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
}))
