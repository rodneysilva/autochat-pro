import { create } from 'zustand'

export type ConversationStatus = 'active' | 'closed' | 'archived'

export interface Customer {
  id: string
  name: string
  phone?: string
  metadata?: Record<string, unknown>
}

export interface Message {
  id: string
  conversationId: string
  role: 'user' | 'bot' | 'human'
  content: string
  mediaType: 'text' | 'image' | 'video' | 'audio' | 'document'
  mediaUrl?: string
  metadata?: Record<string, unknown>
  createdAt: Date
}

export interface Conversation {
  id: string
  botId: string
  customer: Customer
  status: ConversationStatus
  assignedTo: string | null
  lastMessageAt: Date
  lastMessage?: string
  unreadCount: number
  createdAt: Date
  updatedAt: Date
}

interface ConversationsState {
  conversations: Conversation[]
  selectedConversation: Conversation | null
  messages: Message[]
  isLoading: boolean
  error: string | null
  filter: 'all' | 'active' | 'closed' | 'archived'
  setConversations: (conversations: Conversation[]) => void
  setSelectedConversation: (conversation: Conversation | null) => void
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  addConversation: (conversation: Conversation) => void
  updateConversation: (id: string, updates: Partial<Conversation>) => void
  setFilter: (filter: ConversationStatus | 'all') => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useConversationsStore = create<ConversationsState>((set) => ({
  conversations: [],
  selectedConversation: null,
  messages: [],
  isLoading: false,
  error: null,
  filter: 'all',

  setConversations: (conversations) => set({ conversations }),

  setSelectedConversation: (conversation) =>
    set({ selectedConversation: conversation, messages: [] }),

  setMessages: (messages) => set({ messages }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  addConversation: (conversation) =>
    set((state) => ({
      conversations: [conversation, ...state.conversations],
    })),

  updateConversation: (id, updates) =>
    set((state) => ({
      conversations: state.conversations.map((conv) =>
        conv.id === id ? { ...conv, ...updates } : conv
      ),
      selectedConversation:
        state.selectedConversation?.id === id
          ? { ...state.selectedConversation, ...updates }
          : state.selectedConversation,
    })),

  setFilter: (filter) => set({ filter }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),
}))
