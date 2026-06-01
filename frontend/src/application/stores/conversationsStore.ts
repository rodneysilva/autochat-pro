import { create } from 'zustand'
import { conversationsService, type Conversa } from '../../infrastructure/api/conversations.service'

export type ConversationStatus = 'active' | 'closed' | 'archived'

interface ConversationsState {
  conversations: Conversa[]
  selectedConversation: Conversa | null
  isLoading: boolean
  error: string | null
  filter: 'all' | 'active' | 'closed'
  setSelectedConversation: (conversation: Conversa | null) => void
  setFilter: (filter: 'all' | 'active' | 'closed') => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  fetchConversations: (params?: { bot_id?: string; status?: string }) => Promise<void>
}

export const useConversationsStore = create<ConversationsState>((set) => ({
  conversations: [],
  selectedConversation: null,
  isLoading: false,
  error: null,
  filter: 'all',

  setSelectedConversation: (conversation) => set({ selectedConversation: conversation }),
  setFilter: (filter) => set({ filter }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  fetchConversations: async (params) => {
    set({ isLoading: true, error: null })
    try {
      const result = await conversationsService.list(params)
      set({ conversations: result.data, isLoading: false })
    } catch (err: any) {
      const msg = err?.response?.data?.erro?.mensagem || 'Erro ao carregar conversas'
      set({ error: msg, isLoading: false })
    }
  },
}))
