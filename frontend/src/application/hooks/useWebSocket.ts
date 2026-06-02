/**
 * Hook de WebSocket — conecta ao WS quando autenticado,
 * desconecta quando desloga, e atualiza stores em tempo real.
 */

import { useEffect, useRef } from 'react'
import { useAuthStore } from '../stores'
import { useConversationsStore } from '../stores/conversationsStore'
import { wsService } from '../../infrastructure/api/websocket.service'

export function useWebSocket() {
  const token = useAuthStore((s) => s.token)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const fetchConversations = useConversationsStore((s) => s.fetchConversations)
  const prevToken = useRef<string | null>(null)

  useEffect(() => {
    // Conectar quando autenticado com token válido
    if (isAuthenticated && token && token !== prevToken.current) {
      prevToken.current = token
      wsService.connect(token)
    }

    // Desconectar quando desloga
    if (!isAuthenticated) {
      prevToken.current = null
      wsService.disconnect()
    }

    return () => {
      // Cleanup na desmontagem — desconectar se não há outro auth
      // (não desconectar aqui para permitir hot reload)
    }
  }, [isAuthenticated, token])

  useEffect(() => {
    // Escutar mensagens novas → refetch conversas
    const handleMessageNew = () => {
      fetchConversations()
    }

    // Escutar conversa atualizada → refetch conversas
    const handleConversationUpdated = () => {
      fetchConversations()
    }

    // Escutar conversa nova → refetch conversas
    const handleConversationNew = () => {
      fetchConversations()
    }

    wsService.on('message.new', handleMessageNew)
    wsService.on('conversation.updated', handleConversationUpdated)
    wsService.on('conversation.new', handleConversationNew)

    return () => {
      wsService.offEvent('message.new', handleMessageNew)
      wsService.offEvent('conversation.updated', handleConversationUpdated)
      wsService.offEvent('conversation.new', handleConversationNew)
    }
  }, [fetchConversations])
}
