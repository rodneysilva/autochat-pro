import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useBotsStore } from '../../application/stores/botsStore'
import { botsService } from '../../infrastructure/api/bots.service'

export default function BotsPage() {
  const { bots, fetchBots, isLoading } = useBotsStore()
  const [deleting, setDeleting] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null)

  useEffect(() => {
    fetchBots()
  }, [])

  const handlePause = async (botId: string) => {
    try {
      await botsService.pause(botId)
      await fetchBots()
    } catch {}
  }

  const handleResume = async (botId: string) => {
    try {
      await botsService.resume(botId)
      await fetchBots()
    } catch {}
  }

  const handleDelete = async (botId: string) => {
    setDeleting(botId)
    try {
      await botsService.delete(botId)
      await fetchBots()
    } catch {}
    setDeleting(null)
    setShowDeleteConfirm(null)
  }

  const statusColor: Record<string, string> = {
    active: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    paused: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    disconnected: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    connecting: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  }

  const statusLabel: Record<string, string> = {
    active: 'Ativo',
    paused: 'Pausado',
    disconnected: 'Desconectado',
    error: 'Erro',
    connecting: 'Conectando...',
  }

  const statusIcon: Record<string, string> = {
    active: '🟢',
    paused: '🟡',
    disconnected: '⚫',
    error: '🔴',
    connecting: '🔵',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">🤖 Meus Bots</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {bots.length > 0
              ? `${bots.length} bot${bots.length > 1 ? 's' : ''} configurado${bots.length > 1 ? 's' : ''}`
              : 'Conecte seu primeiro WhatsApp para começar!'
            }
          </p>
        </div>
        <Link
          to="/add-bot"
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition font-medium"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Adicionar Bot
        </Link>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {/* Lista de bots */}
      {!isLoading && bots.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {bots.map(bot => (
            <div
              key={bot.id}
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-md transition"
            >
              {/* Card header */}
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
                      {bot.tipo === 'whatsapp' ? (
                        <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.548-.237 0 0-.579-.657-.853-.967-.273-.31-.548-.099-.548-.099l.001.001c-.452-.198-.922-.361-1.386-.498-.198-.039-.374-.058-.548-.058-.297 0-.688.099-1.097.297-.498.298-.907.696-1.236 1.097-.249.298-.548.597-.896.696-.298.099-.548.199-.847.199-.846 0-1.097-.199-1.595-.597l-1.097.597c.498.796.996 1.593 1.495 2.39l1.495-2.39zM12 2C6.477 2 2 6.477 2 12c0 1.89.525 3.66 1.438 5.168L2 22l4.832-1.438A9.955 9.955 0 0012 22c5.523 0 10-4.477 10-10S17.523 2 12 2z"/>
                        </svg>
                      ) : (
                        <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      )}
                    </div>
                    <div className="min-w-0">
                      <h3 className="font-semibold text-gray-900 dark:text-white truncate">{bot.nome}</h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {bot.tipo === 'whatsapp' ? 'WhatsApp' : 'Telegram'}
                      </p>
                    </div>
                  </div>
                  <span className={`px-2.5 py-1 text-xs font-medium rounded-full flex-shrink-0 ${statusColor[bot.status] || ''}`}>
                    {statusIcon[bot.status]} {statusLabel[bot.status] || bot.status}
                  </span>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">{bot.estatisticas?.total_mensagens || 0}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Mensagens</p>
                  </div>
                  <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">{bot.estatisticas?.total_conversas || 0}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Conversas</p>
                  </div>
                  <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                      {bot.llm_config?.ativado ? '✅' : '❌'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">IA Ativa</p>
                  </div>
                </div>

                {/* Badges informativos */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {bot.mensagem_boas_vindas && (
                    <span className="px-2 py-0.5 text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-full">
                      💬 Saudação
                    </span>
                  )}
                  {bot.working_hours?.ativado && (
                    <span className="px-2 py-0.5 text-xs bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400 rounded-full">
                      🕐 Horário
                    </span>
                  )}
                  {bot.llm_config?.ativado && (
                    <span className="px-2 py-0.5 text-xs bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded-full">
                      ⚡ IA GLM
                    </span>
                  )}
                </div>

                {/* Ações */}
                <div className="flex items-center gap-2">
                  <Link
                    to={`/bots/${bot.id}/config`}
                    className="flex-1 py-2 text-center text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium"
                  >
                    ⚙️ Configurar
                  </Link>

                  {bot.status === 'active' && (
                    <button
                      onClick={() => handlePause(bot.id)}
                      className="flex-1 py-2 text-sm border border-yellow-300 dark:border-yellow-600 text-yellow-700 dark:text-yellow-400 rounded-lg hover:bg-yellow-50 dark:hover:bg-yellow-900/30 transition font-medium"
                    >
                      ⏸️ Pausar
                    </button>
                  )}

                  {bot.status === 'paused' && (
                    <button
                      onClick={() => handleResume(bot.id)}
                      className="flex-1 py-2 text-sm border border-green-300 dark:border-green-600 text-green-700 dark:text-green-400 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/30 transition font-medium"
                    >
                      ▶️ Retomar
                    </button>
                  )}

                  <button
                    onClick={() => setShowDeleteConfirm(bot.id)}
                    className="px-3 py-2 text-sm border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 transition"
                    title="Deletar bot"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              {/* Modal de confirmação de exclusão */}
              {showDeleteConfirm === bot.id && (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800">
                  <p className="text-sm text-red-700 dark:text-red-400 mb-3">
                    Tem certeza que deseja deletar <strong>{bot.nome}</strong>? Esta ação não pode ser desfeita e a instância WhatsApp será removida.
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDelete(bot.id)}
                      disabled={deleting === bot.id}
                      className="flex-1 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium disabled:opacity-50"
                    >
                      {deleting === bot.id ? 'Deletando...' : 'Sim, Deletar'}
                    </button>
                    <button
                      onClick={() => setShowDeleteConfirm(null)}
                      className="flex-1 py-2 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Estado vazio */}
      {!isLoading && bots.length === 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 lg:p-12 text-center">
          <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Nenhum bot conectado</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md mx-auto">
            Conecte seu primeiro WhatsApp para começar a receber mensagens automaticamente com IA.
          </p>
          <Link
            to="/add-bot"
            className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Conectar WhatsApp
          </Link>

          {/* Quick guide */}
          <div className="mt-8 pt-8 border-t border-gray-100 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">Como funciona?</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
              <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-lg mb-1">📱</div>
                <p className="text-xs font-medium text-gray-900 dark:text-white">1. Conecte</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Vincule seu WhatsApp via QR Code ou telefone</p>
              </div>
              <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-lg mb-1">⚙️</div>
                <p className="text-xs font-medium text-gray-900 dark:text-white">2. Configure</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Defina mensagens e ative a IA GLM</p>
              </div>
              <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-lg mb-1">🤖</div>
                <p className="text-xs font-medium text-gray-900 dark:text-white">3. Automatize</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">O bot responde automaticamente 24/7</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
