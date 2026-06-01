import { useEffect, useState } from 'react'
import { plansService, type PlanConfig, type CurrentPlanResponse } from '../../infrastructure/api/plans.service'

export default function PricingPage() {
  const [plans, setPlans] = useState<PlanConfig[]>([])
  const [currentPlan, setCurrentPlan] = useState<CurrentPlanResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState('')
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    loadPlans()
  }, [])

  const loadPlans = async () => {
    setLoading(true)
    try {
      const [plansRes, currentRes] = await Promise.all([
        plansService.list(),
        plansService.getCurrent(),
      ])
      setPlans(plansRes.plans)
      setCurrentPlan(currentRes)
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.erro?.mensagem || 'Erro ao carregar planos')
    } finally {
      setLoading(false)
    }
  }

  const handleUpgrade = async (planType: string) => {
    setUpgrading(planType)
    setSuccessMsg('')
    setErrorMsg('')
    try {
      const result = await plansService.upgrade(planType)
      setSuccessMsg(result.message)
      await loadPlans()
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.erro?.mensagem || 'Erro ao atualizar plano')
    } finally {
      setUpgrading(null)
    }
  }

  const planColors: Record<string, { border: string; badge: string; btn: string; bg: string }> = {
    free: {
      border: 'border-gray-200 dark:border-gray-700',
      badge: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
      btn: 'bg-gray-600 text-white hover:bg-gray-700',
      bg: 'bg-white dark:bg-gray-800',
    },
    basic: {
      border: 'border-blue-300 dark:border-blue-700',
      badge: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      btn: 'bg-blue-600 text-white hover:bg-blue-700',
      bg: 'bg-white dark:bg-gray-800',
    },
    pro: {
      border: 'border-purple-400 dark:border-purple-600',
      badge: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
      btn: 'bg-purple-600 text-white hover:bg-purple-700',
      bg: 'bg-gradient-to-b from-purple-50 to-white dark:from-purple-900/10 dark:to-gray-800',
    },
  }

  const planLabels: Record<string, string> = { free: 'Gratuito', basic: 'Basic', pro: 'Profissional' }
  const planPrices: Record<string, string> = { free: 'R$ 0', basic: 'R$ 49/mês', pro: 'R$ 149/mês' }
  const planOrder = ['free', 'basic', 'pro']

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">💎 Planos e Preços</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-lg mx-auto">
          Escolha o plano ideal para o seu negócio. Todos incluem 14 dias de teste grátis.
        </p>
      </div>

      {/* Mensagens */}
      {successMsg && (
        <div className="max-w-2xl mx-auto p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-sm text-green-600 dark:text-green-400">✅ {successMsg}</p>
        </div>
      )}
      {errorMsg && (
        <div className="max-w-2xl mx-auto p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{errorMsg}</p>
        </div>
      )}

      {/* Plano atual */}
      {currentPlan && (
        <div className="max-w-2xl mx-auto bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-600 dark:text-purple-400 font-medium">Seu plano atual</p>
              <p className="text-lg font-bold text-gray-900 dark:text-white capitalize">
                {planLabels[currentPlan.tipo] || currentPlan.tipo}
              </p>
            </div>
            <div className="text-right text-sm text-gray-600 dark:text-gray-400">
              <p>📱 {currentPlan.usage.bots}/{currentPlan.max_bots === -1 ? '∞' : currentPlan.max_bots} bots</p>
              <p>👥 {currentPlan.usage.contacts}/{currentPlan.max_contatos === -1 ? '∞' : currentPlan.max_contatos} contatos</p>
            </div>
          </div>
        </div>
      )}

      {/* Cards de planos */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {planOrder.map(planType => {
          const plan = plans.find(p => p.tipo === planType)
          if (!plan) return null

          const colors = planColors[planType] || planColors.free
          const isCurrent = currentPlan?.tipo === planType
          const canUpgrade = currentPlan && planOrder.indexOf(planType) > planOrder.indexOf(currentPlan.tipo)

          return (
            <div
              key={planType}
              className={`rounded-xl border-2 p-6 relative ${colors.border} ${colors.bg} ${
                isCurrent ? 'ring-2 ring-purple-500' : ''
              }`}
            >
              {/* Badge */}
              <div className="flex items-center justify-between mb-4">
                <span className={`px-3 py-1 text-xs font-medium rounded-full ${colors.badge}`}>
                  {planLabels[planType]}
                </span>
                {isCurrent && (
                  <span className="px-2 py-1 text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded-full">
                    Atual
                  </span>
                )}
              </div>

              {/* Preço */}
              <div className="mb-6">
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{planPrices[planType]}</p>
              </div>

              {/* Limites */}
              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-purple-500">🤖</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    {plan.max_bots === -1 ? 'Bots ilimitados' : `${plan.max_bots} bot${plan.max_bots > 1 ? 's' : ''}`}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-purple-500">📨</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    {plan.max_messages_per_month === -1 ? 'Mensagens ilimitadas' : `${plan.max_messages_per_month.toLocaleString('pt-BR')} mensagens/mês`}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-purple-500">👥</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    {plan.max_contacts === -1 ? 'Contatos ilimitados' : `${plan.max_contacts.toLocaleString('pt-BR')} contatos`}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-purple-500">💬</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    {plan.max_conversations === -1 ? 'Conversas ilimitadas' : `${plan.max_conversations} conversas`}
                  </span>
                </div>
              </div>

              {/* Features */}
              <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mb-6">
                <ul className="space-y-2">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Botão */}
              <button
                onClick={() => canUpgrade ? handleUpgrade(planType) : undefined}
                disabled={!canUpgrade || upgrading === planType}
                className={`w-full py-3 rounded-lg font-medium text-sm transition ${
                  isCurrent
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-default'
                    : canUpgrade
                    ? `${colors.btn}`
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                }`}
              >
                {upgrading === planType ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Atualizando...
                  </span>
                ) : isCurrent ? (
                  'Plano Atual'
                ) : (
                  `Fazer Upgrade`
                )}
              </button>
            </div>
          )
        })}
      </div>

      {/* FAQ */}
      <div className="max-w-2xl mx-auto mt-8">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white text-center mb-4">Perguntas Frequentes</h3>
        <div className="space-y-3">
          <details className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <summary className="p-4 text-sm font-medium text-gray-900 dark:text-white cursor-pointer">
              Posso cancelar a qualquer momento?
            </summary>
            <p className="px-4 pb-4 text-sm text-gray-600 dark:text-gray-400">
              Sim! Você pode cancelar seu plano a qualquer momento. Seu plano volta para o gratuito no próximo ciclo.
            </p>
          </details>
          <details className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <summary className="p-4 text-sm font-medium text-gray-900 dark:text-white cursor-pointer">
              O que acontece se ultrapassar o limite de mensagens?
            </summary>
            <p className="px-4 pb-4 text-sm text-gray-600 dark:text-gray-400">
              O bot continua respondendo, mas você será notificado para fazer upgrade. No plano Free, após 100 mensagens o bot pausa automaticamente.
            </p>
          </details>
          <details className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <summary className="p-4 text-sm font-medium text-gray-900 dark:text-white cursor-pointer">
              Posso testar antes de pagar?
            </summary>
            <p className="px-4 pb-4 text-sm text-gray-600 dark:text-gray-400">
              Sim! Todos os planos incluem 14 dias de teste grátis com todas as funcionalidades do plano Pro.
            </p>
          </details>
        </div>
      </div>
    </div>
  )
}
