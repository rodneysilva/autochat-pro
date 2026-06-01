import { Link } from 'react-router-dom'
import { useAuthStore } from '../../application/stores'

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  const stats = [
    { label: 'Bots Ativos', value: '0', icon: '🤖', color: 'purple' },
    { label: 'Conversas Hoje', value: '0', icon: '💬', color: 'blue' },
    { label: 'Mensagens', value: '0', icon: '📨', color: 'green' },
    { label: 'Resposta IA', value: '-', icon: '⚡', color: 'emerald' },
  ]

  const colorClasses: Record<string, string> = {
    purple: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800',
    blue: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
    green: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    emerald: 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800',
  }

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-6 text-white">
        <h2 className="text-xl font-bold mb-1">
          Olá, {user?.nome || 'Usuário'}! 👋
        </h2>
        <p className="text-purple-100 text-sm">
          Bem-vindo ao AutoChat Pro. Comece conectando seu primeiro bot WhatsApp.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className={`rounded-xl p-4 lg:p-6 border ${colorClasses[stat.color]}`}>
            <div className="text-2xl mb-2">{stat.icon}</div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</h3>
            <p className="text-xs lg:text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Setup Guide - WhatsApp */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="p-5 lg:p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">🚀 Comece Aqui</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Siga os passos para configurar seu primeiro bot</p>
        </div>

        <div className="divide-y divide-gray-100 dark:divide-gray-700">
          {/* Step 1 */}
          <div className="p-5 lg:p-6 flex items-start gap-4">
            <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.548-.548-.237 0 0-.579-.657-.853-.967-.273-.31-.548-.099-.548-.099l.001.001c-.452-.198-.922-.361-1.386-.498-.198-.039-.374-.058-.548-.058-.297 0-.688.099-1.097.297-.498.298-.907.696-1.236 1.097-.249.298-.548.597-.896.696-.298.099-.548.199-.847.199-.846 0-1.097-.199-1.595-.597l-1.097.597c.498.796.996 1.593 1.495 2.39l1.495-2.39z"/>
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-gray-900 dark:text-white">1. Conectar WhatsApp</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Crie uma instância e conecte seu WhatsApp via QR Code ou número de telefone.
              </p>
              <Link
                to="/add-bot"
                className="inline-flex items-center gap-1.5 mt-3 px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition font-medium"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Adicionar Bot WhatsApp
              </Link>
            </div>
          </div>

          {/* Step 2 */}
          <div className="p-5 lg:p-6 flex items-start gap-4 opacity-50">
            <div className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-gray-900 dark:text-white">2. Criar Automações</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Configure respostas automáticas, palavras-chave e mensagens de boas-vindas.
              </p>
              <span className="inline-block mt-3 text-xs text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-700 px-3 py-1.5 rounded-lg">
                Em breve
              </span>
            </div>
          </div>

          {/* Step 3 */}
          <div className="p-5 lg:p-6 flex items-start gap-4 opacity-50">
            <div className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-gray-900 dark:text-white">3. Ativar IA</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Integre GLM para respostas inteligentes e atendimento automático 24/7.
              </p>
              <span className="inline-block mt-3 text-xs text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-700 px-3 py-1.5 rounded-lg">
                Em breve
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Link to="/add-bot" className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:border-green-300 dark:hover:border-green-700 transition">
          <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mb-3">
            <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
          <p className="font-medium text-gray-900 dark:text-white text-sm">Adicionar Bot</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">WhatsApp</p>
        </Link>

        <Link to="/automations" className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:border-blue-300 dark:hover:border-blue-700 transition">
          <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-3">
            <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <p className="font-medium text-gray-900 dark:text-white text-sm">Automações</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Regras</p>
        </Link>

        <Link to="/analytics" className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:border-purple-300 dark:hover:border-purple-700 transition">
          <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mb-3">
            <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="font-medium text-gray-900 dark:text-white text-sm">Analytics</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Relatórios</p>
        </Link>

        <Link to="/settings" className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:border-orange-300 dark:hover:border-orange-700 transition">
          <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center mb-3">
            <svg className="w-5 h-5 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <p className="font-medium text-gray-900 dark:text-white text-sm">Configurações</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Ajustes</p>
        </Link>
      </div>

      {/* Plano atual */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Plano Atual</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white capitalize">{user?.plano?.tipo || 'Free'}</p>
          </div>
          <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 text-xs font-medium rounded-full">
            Ativo
          </span>
        </div>
      </div>
    </div>
  )
}
