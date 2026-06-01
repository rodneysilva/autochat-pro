import { useEffect } from 'react'
import { useConversationsStore } from '../../application/stores/conversationsStore'

export default function ConversationsPage() {
  const { conversations, isLoading, error, filter, setFilter, fetchConversations } = useConversationsStore()

  useEffect(() => {
    const params: Record<string, string> = {}
    if (filter !== 'all') params.status = filter
    fetchConversations(params)
  }, [filter])

  const statusColor: Record<string, string> = {
    active: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    waiting: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    closed: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400',
    archived: 'bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500',
  }

  const statusLabel: Record<string, string> = {
    active: 'Ativa',
    waiting: 'Aguardando',
    closed: 'Fechada',
    archived: 'Arquivada',
  }

  const filterTabs: { key: 'all' | 'active' | 'closed'; label: string }[] = [
    { key: 'all', label: 'Todas' },
    { key: 'active', label: 'Ativas' },
    { key: 'closed', label: 'Fechadas' },
  ]

  const formatRelativeTime = (dateStr: string | null) => {
    if (!dateStr) return '—'
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMin = Math.floor(diffMs / 60000)
    const diffHr = Math.floor(diffMs / 3600000)
    const diffDay = Math.floor(diffMs / 86400000)

    if (diffMin < 1) return 'agora'
    if (diffMin < 60) return `${diffMin}min atrás`
    if (diffHr < 24) return `${diffHr}h atrás`
    if (diffDay < 7) return `${diffDay}d atrás`
    return date.toLocaleDateString('pt-BR')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">💬 Conversas</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {conversations.length > 0
            ? `${conversations.length} conversa${conversations.length > 1 ? 's' : ''}`
            : 'Nenhuma conversa registrada ainda'
          }
        </p>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2">
        {filterTabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition ${
              filter === tab.key
                ? 'bg-purple-600 text-white'
                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Lista de conversas */}
      {!isLoading && conversations.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {conversations.map(conv => (
              <div
                key={conv.id}
                className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    {/* Avatar */}
                    <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-purple-600 dark:text-purple-400 font-medium text-sm">
                        {(conv.cliente?.nome || conv.cliente?.id || '?').charAt(0).toUpperCase()}
                      </span>
                    </div>
                    {/* Info */}
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-900 dark:text-white truncate">
                          {conv.cliente?.nome || conv.cliente?.id || 'Desconhecido'}
                        </p>
                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0 ${statusColor[conv.status] || ''}`}>
                          {statusLabel[conv.status] || conv.status}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                        {conv.cliente?.telefone || conv.cliente?.id || '—'} · {formatRelativeTime(conv.ultima_mensagem_em)}
                      </p>
                    </div>
                  </div>
                  {/* Bot badge */}
                  <div className="flex-shrink-0 ml-4">
                    <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
                      🤖
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Estado vazio */}
      {!isLoading && conversations.length === 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 lg:p-12 text-center">
          <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Nenhuma conversa</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md mx-auto">
            {filter !== 'all'
              ? `Nenhuma conversa ${statusLabel[filter]?.toLowerCase() || filter} encontrada.`
              : 'As conversas dos seus bots aparecerão aqui. Conecte um bot e ative a IA para começar a receber mensagens.'
            }
          </p>
          {filter !== 'all' && (
            <button
              onClick={() => setFilter('all')}
              className="text-purple-600 dark:text-purple-400 hover:underline text-sm font-medium"
            >
              Ver todas as conversas
            </button>
          )}
        </div>
      )}
    </div>
  )
}
