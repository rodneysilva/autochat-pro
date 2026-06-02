import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { botsService } from '../../infrastructure/api/bots.service'
import { whatsappService, ConnectionStatus } from '../../infrastructure/api/whatsapp.service'
import { useBotsStore } from '../../application/stores/botsStore'

type Tab = 'mensagens' | 'horario' | 'whatsapp' | 'ia'

export default function BotConfigPage() {
  const { botId } = useParams<{ botId: string }>()
  const navigate = useNavigate()
  const { bots, fetchBots, updateBot } = useBotsStore()
  const [activeTab, setActiveTab] = useState<Tab>('mensagens')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Buscar dados do bot
  const bot = bots.find(b => b.id === botId) || null

  // States dos campos editáveis
  const [nome, setNome] = useState('')
  const [mensagemBoasVindas, setMensagemBoasVindas] = useState('')
  const [mensagemDespedida, setMensagemDespedida] = useState('')
  const [mensagemRespostaPadrao, setMensagemRespostaPadrao] = useState('')

  // Working hours
  const [whAtivado, setWhAtivado] = useState(false)
  const [whInicio, setWhInicio] = useState('08:00')
  const [whFim, setWhFim] = useState('18:00')
  const [whTimezone, setWhTimezone] = useState('America/Sao_Paulo')
  const [whMensagemFora, setWhMensagemFora] = useState('')

  // LLM Config
  const [llmAtivado, setLlmAtivado] = useState(false)
  const [llmProvider, setLlmProvider] = useState('glm')
  const [llmModelo, setLlmModelo] = useState('glm-4-flash')
  const [llmTemperatura, setLlmTemperatura] = useState(0.7)
  const [llmMaxTokens, setLlmMaxTokens] = useState(2048)
  const [llmSystemPrompt, setLlmSystemPrompt] = useState('')
  const [llmMaxContextMessages, setLlmMaxContextMessages] = useState(20)

  // WhatsApp reconnect states
  const [waMethod, setWaMethod] = useState<'qrcode' | 'phone'>('qrcode')
  const [waStatus, setWaStatus] = useState<'idle' | 'connecting' | 'qrcode' | 'pairing' | 'connected' | 'error'>('idle')
  const [waQrCode, setWaQrCode] = useState<string | null>(null)
  const [waPairingCode, setWaPairingCode] = useState<string | null>(null)
  const [waPhone, setWaPhone] = useState('')
  const [waError, setWaError] = useState('')
  const [waTimeLeft, setWaTimeLeft] = useState(180)
  const waPollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const waTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const [waLoading, setWaLoading] = useState(false)
  const [waSuccess, setWaSuccess] = useState(false)

  useEffect(() => {
    fetchBots()
  }, [])

  useEffect(() => {
    if (bots.length > 0 && !bot && botId) {
      // Bot não encontrado nos bots do usuário
      setLoading(false)
      setError('Bot não encontrado')
    } else if (bot) {
      // Preencher campos com dados do bot
      setNome(bot.nome)
      setMensagemBoasVindas(bot.mensagem_boas_vindas || '')
      setMensagemDespedida(bot.mensagem_despedida || '')
      setMensagemRespostaPadrao(bot.mensagem_resposta_padrao || '')

      setWhAtivado(bot.working_hours?.ativado || false)
      setWhInicio(bot.working_hours?.inicio || '08:00')
      setWhFim(bot.working_hours?.fim || '18:00')
      setWhTimezone(bot.working_hours?.timezone || 'America/Sao_Paulo')
      setWhMensagemFora(bot.working_hours?.mensagem_fora_horario || '')

      setLlmAtivado(bot.llm_config?.ativado || false)
      setLlmProvider(bot.llm_config?.provider || 'glm')
      setLlmModelo(bot.llm_config?.modelo || 'glm-4-flash')
      setLlmTemperatura(bot.llm_config?.temperatura ?? 0.7)
      setLlmMaxTokens(bot.llm_config?.max_tokens || 2048)
      setLlmSystemPrompt(bot.llm_config?.system_prompt || '')
      setLlmMaxContextMessages(bot.llm_config?.max_context_messages || 20)

      setLoading(false)
    }
  }, [bot, botId, bots.length])

  // Verificar status real da Evolution ao abrir aba WhatsApp
  useEffect(() => {
    if (bot?.nome && activeTab === 'whatsapp') {
      whatsappService.getStatus(bot.nome)
        .then(r => {
          if (!r.connected && bot.status === 'active') {
            // Evolution desconectada mas banco diz ativo → sincronizar
            botsService.pause(bot.id).then(() => fetchBots()).catch(() => {})
          }
        })
        .catch(() => {})
    }
  }, [bot?.nome, activeTab])

  // Cleanup WhatsApp polling/timer on unmount
  useEffect(() => {
    return () => {
      if (waPollRef.current) clearInterval(waPollRef.current)
      if (waTimerRef.current) clearInterval(waTimerRef.current)
    }
  }, [])

  const startWaStatusPoll = (instance: string, botId: string) => {
    let pollCount = 0
    const MAX_POLLS = 90

    // Timer countdown
    setWaTimeLeft(180)
    waTimerRef.current = setInterval(() => {
      setWaTimeLeft(prev => {
        if (prev <= 1) {
          if (waTimerRef.current) clearInterval(waTimerRef.current)
          if (waPollRef.current) clearInterval(waPollRef.current)
          setWaStatus('error')
          setWaError('Tempo esgotado. O código expirou. Tente novamente.')
          return 0
        }
        return prev - 1
      })
    }, 1000)

    waPollRef.current = setInterval(async () => {
      pollCount++
      try {
        // Primary: getStatus
        let isConnected = false
        try {
          const statusResult = await whatsappService.getStatus(instance)
          if (statusResult.connected) {
            isConnected = true
          }
        } catch {}

        // Fallback: checkPhoneStatus
        if (!isConnected) {
          try {
            const phoneResult = await whatsappService.checkPhoneStatus(instance)
            if ((phoneResult.status as string) !== 'pairing' && (phoneResult.status as string) !== 'disconnected') {
              isConnected = true
            }
          } catch {}
        }

        if (isConnected) {
          if (waPollRef.current) clearInterval(waPollRef.current)
          if (waTimerRef.current) clearInterval(waTimerRef.current)
          setWaStatus('connected')
          setWaQrCode(null)
          setWaPairingCode(null)
          try {
            await botsService.resume(botId)
            await fetchBots()
          } catch (err) {
            console.error('Erro ao ativar bot:', err)
          }
          setWaSuccess(true)
          setTimeout(() => navigate('/dashboard'), 2000)
          return
        }

        if (pollCount >= MAX_POLLS) {
          if (waPollRef.current) clearInterval(waPollRef.current)
          if (waTimerRef.current) clearInterval(waTimerRef.current)
          setWaStatus('error')
          setWaError('Tempo esgotado. O código expirou. Tente novamente.')
        }
      } catch (err: any) {
        if (err?.response?.status === 404) {
          if (waPollRef.current) clearInterval(waPollRef.current)
          if (waTimerRef.current) clearInterval(waTimerRef.current)
          setWaStatus('error')
          setWaError('Instância não encontrada. Tente novamente.')
        }
      }
    }, 2000)
  }

  const handleWaReset = () => {
    if (waPollRef.current) clearInterval(waPollRef.current)
    if (waTimerRef.current) clearInterval(waTimerRef.current)
    setWaStatus('idle')
    setWaQrCode(null)
    setWaPairingCode(null)
    setWaError('')
    setWaPhone('')
    setWaTimeLeft(180)
    setWaSuccess(false)
  }

  const handleSave = async () => {
    if (!botId) return
    setSaving(true)
    setSaved(false)
    setError('')

    try {
      // Montar payload com campos alterados
      const data: Record<string, any> = {}

      if (activeTab === 'mensagens') {
        data.nome = nome
        data.mensagem_boas_vindas = mensagemBoasVindas
        data.mensagem_despedida = mensagemDespedida
        data.mensagem_resposta_padrao = mensagemRespostaPadrao
      } else if (activeTab === 'horario') {
        data.working_hours_ativado = whAtivado
        data.working_hours_inicio = whInicio
        data.working_hours_fim = whFim
        data.working_hours_timezone = whTimezone
        data.working_hours_mensagem_fora = whMensagemFora
      } else if (activeTab === 'ia') {
        data.llm_ativado = llmAtivado
        data.llm_provider = llmProvider
        data.llm_modelo = llmModelo
        data.llm_temperatura = llmTemperatura
        data.llm_max_tokens = llmMaxTokens
        data.llm_system_prompt = llmSystemPrompt
        data.llm_max_context_messages = llmMaxContextMessages
      }

      const result = await botsService.update(botId, data)
      updateBot(botId, {
        nome: result.nome,
        mensagem_boas_vindas: result.mensagem_boas_vindas,
        mensagem_despedida: result.mensagem_despedida,
        mensagem_resposta_padrao: result.mensagem_resposta_padrao,
        working_hours: result.working_hours,
        llm_config: result.llm_config,
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err: any) {
      setError(err?.response?.data?.erro?.mensagem || 'Erro ao salvar configuração')
    } finally {
      setSaving(false)
    }
  }

  const tabs: { key: Tab; label: string; icon: string }[] = [
    { key: 'mensagens', label: 'Mensagens', icon: '💬' },
    { key: 'horario', label: 'Horário', icon: '🕐' },
    { key: 'whatsapp', label: 'WhatsApp', icon: '📱' },
    { key: 'ia', label: 'IA (LLM)', icon: '⚡' },
  ]

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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  if (error && !bot) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-16 h-16 bg-red-50 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Bot não encontrado</h2>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Este bot não existe ou não pertence a você.</p>
        <Link to="/dashboard" className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
          Voltar ao Dashboard
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
          >
            <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">{nome}</h1>
              {bot && (
                <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${statusColor[bot.status] || ''}`}>
                  {statusLabel[bot.status] || bot.status}
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {bot?.tipo === 'whatsapp' ? '📱 WhatsApp' : '✈️ Telegram'} · Configurações
            </p>
          </div>
        </div>

        {/* Botão salvar */}
        <button
          onClick={handleSave}
          disabled={saving}
          className={`px-5 py-2.5 rounded-lg font-medium text-sm transition flex items-center gap-2 ${
            saved
              ? 'bg-green-600 text-white'
              : 'bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50'
          }`}
        >
          {saving ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Salvando...
            </>
          ) : saved ? (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Salvo!
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Salvar
            </>
          )}
        </button>
      </div>

      {/* Toast de erro */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex gap-1 -mb-px">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition ${
                activeTab === tab.key
                  ? 'border-purple-600 text-purple-600 dark:text-purple-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <span className="mr-1.5">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab: Mensagens */}
      {activeTab === 'mensagens' && (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 lg:p-6 space-y-6">
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Mensagens Automáticas</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Configure as mensagens que seu bot envia automaticamente. Use variáveis como <code className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs">{`{nome}`}</code> para personalizar.
              </p>
            </div>

            {/* Nome do Bot */}
            <div>
              <label htmlFor="botName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nome do Bot
              </label>
              <input
                id="botName"
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Ex: Bot Atendimento Principal"
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Nome interno para identificar o bot. Não afeta as mensagens enviadas.
              </p>
            </div>

            {/* Mensagem de boas-vindas */}
            <div>
              <label htmlFor="msgBoasVindas" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                💬 Mensagem de Boas-vindas
              </label>
              <textarea
                id="msgBoasVindas"
                rows={4}
                value={mensagemBoasVindas}
                onChange={(e) => setMensagemBoasVindas(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-y"
                placeholder="Olá! Bem-vindo à [nome da empresa]. Como posso ajudar?"
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                💡 Enviada automaticamente quando um cliente inicia uma conversa. Inclua saudação e informe o que o bot pode fazer.
              </p>
              <details className="mt-2">
                <summary className="text-xs text-purple-600 dark:text-purple-400 cursor-pointer hover:underline">
                  Ver exemplos
                </summary>
                <div className="mt-2 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-xs text-gray-600 dark:text-gray-400 space-y-1.5">
                  <p>📦 <strong>E-commerce:</strong> "Olá! Bem-vindo à Loja XYZ! 🛍️ Posso ajudar com pedidos, prazos de entrega ou trocas. Como posso ajudar?"</p>
                  <p>🍕 <strong>Restaurante:</strong> "Oi! 👋 Bem-vindo ao Restaurante ABC! Cardápio do dia, horário de funcionamento ou reservas — é só falar!"</p>
                  <p>🏥 <strong>Clínica:</strong> "Olá! 🏥 Clínica Saúde+. Posso agendar consultas, informar horários ou tirar dúvidas. Como posso ajudar?"</p>
                </div>
              </details>
            </div>

            {/* Mensagem de despedida */}
            <div>
              <label htmlFor="msgDespedida" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                👋 Mensagem de Despedida
              </label>
              <textarea
                id="msgDespedida"
                rows={3}
                value={mensagemDespedida}
                onChange={(e) => setMensagemDespedida(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-y"
                placeholder="Obrigado pelo contato! Até breve."
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                💡 Enviada ao finalizar a conversa ou quando o cliente fica inativo por muito tempo.
              </p>
            </div>

            {/* Mensagem de resposta padrão */}
            <div>
              <label htmlFor="msgRespostaPadrao" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                🤖 Mensagem de Resposta Padrão (sem IA)
              </label>
              <textarea
                id="msgRespostaPadrao"
                rows={3}
                value={mensagemRespostaPadrao}
                onChange={(e) => setMensagemRespostaPadrao(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-y"
                placeholder="Obrigado pela mensagem! Vou analisar e responder em breve."
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                💡 Usada quando a IA (GLM) está <strong>desativada</strong>. Se a IA estiver ativa, o prompt do sistema define as respostas.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Horário */}
      {activeTab === 'horario' && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 lg:p-6 space-y-6">
          <div>
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Horário de Funcionamento</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Defina quando o bot deve responder automaticamente. Fora do horário, envie uma mensagem personalizada.
            </p>
          </div>

          {/* Toggle */}
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900 dark:text-white">Ativar horário de funcionamento</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                O bot só responde dentro do horário definido
              </p>
            </div>
            <button
              onClick={() => setWhAtivado(!whAtivado)}
              className={`relative w-12 h-6 rounded-full transition-colors ${whAtivado ? 'bg-purple-600' : 'bg-gray-300 dark:bg-gray-600'}`}
            >
              <span
                className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${whAtivado ? 'translate-x-6' : ''}`}
              />
            </button>
          </div>

          {whAtivado && (
            <>
              {/* Horários */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="whInicio" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Início
                  </label>
                  <input
                    id="whInicio"
                    type="time"
                    value={whInicio}
                    onChange={(e) => setWhInicio(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label htmlFor="whFim" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Fim
                  </label>
                  <input
                    id="whFim"
                    type="time"
                    value={whFim}
                    onChange={(e) => setWhFim(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              {/* Timezone */}
              <div>
                <label htmlFor="whTimezone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Fuso horário
                </label>
                <select
                  id="whTimezone"
                  value={whTimezone}
                  onChange={(e) => setWhTimezone(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="America/Sao_Paulo">São Paulo (UTC-3)</option>
                  <option value="America/Manaus">Manaus (UTC-4)</option>
                  <option value="America/Belem">Belém (UTC-3)</option>
                  <option value="America/Fortaleza">Fortaleza (UTC-3)</option>
                  <option value="America/Recife">Recife (UTC-3)</option>
                  <option value="America/Cuiaba">Cuiabá (UTC-4)</option>
                  <option value="America/Porto_Velho">Porto Velho (UTC-4)</option>
                  <option value="America/Rio_Branco">Rio Branco (UTC-5)</option>
                  <option value="America/Noronha">Fernando de Noronha (UTC-2)</option>
                </select>
              </div>

              {/* Mensagem fora de horário */}
              <div>
                <label htmlFor="whMensagemFora" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  🌙 Mensagem fora do horário
                </label>
                <textarea
                  id="whMensagemFora"
                  rows={3}
                  value={whMensagemFora}
                  onChange={(e) => setWhMensagemFora(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-y"
                  placeholder="Olá! Nosso horário de atendimento é das 08:00 às 18:00. Responderemos sua mensagem assim que possível."
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  💡 Enviada quando um cliente manda mensagem fora do horário de funcionamento.
                </p>
                <details className="mt-2">
                  <summary className="text-xs text-purple-600 dark:text-purple-400 cursor-pointer hover:underline">
                    Ver exemplos
                  </summary>
                  <div className="mt-2 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-xs text-gray-600 dark:text-gray-400 space-y-1.5">
                    <p>🛒 <strong>E-commerce:</strong> "Oi! 👋 Nosso horário de atendimento é das 8h às 18h (seg-sex). Seu pedido pode ser feito 24h pelo nosso site!"</p>
                    <p>🍕 <strong>Restaurante:</strong> "Olá! 🍕 Funcionamos das 11h às 22h. Pedidos online estão disponíveis durante todo o horário de funcionamento!"</p>
                    <p>🏥 <strong>Clínica:</strong> "Boa noite! 🏥 Nosso horário é das 7h às 20h. Para emergências, ligue para (XX) XXXXX-XXXX."</p>
                  </div>
                </details>
              </div>
            </>
          )}

          {!whAtivado && (
            <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
              <p className="text-sm text-yellow-700 dark:text-yellow-400">
                ⚠️ Com o horário desativado, o bot responde <strong>24 horas por dia</strong>, incluindo fins de semana e feriados.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab: WhatsApp */}
      {activeTab === 'whatsapp' && (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 lg:p-6 space-y-6">
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Conexão WhatsApp</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Gerencie a conexão do WhatsApp desta instância.
              </p>
            </div>

            {/* Status badge */}
            {bot && (
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1.5 text-sm font-medium rounded-full ${statusColor[bot.status] || ''}`}>
                  {statusLabel[bot.status] || bot.status}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Instância: <code className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs">{bot.nome}</code>
                </span>
              </div>
            )}

            {/* Active / Connecting state */}
            {bot && (bot.status === 'active' || bot.status === 'connecting') && (
              <div className="space-y-4">
                {bot.status === 'active' ? (
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-2.5 h-2.5 bg-green-500 rounded-full"></div>
                      <span className="text-sm font-medium text-green-700 dark:text-green-400">Conectado</span>
                    </div>
                    {bot.ultimo_conectado_em && (
                      <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                        Conectado em {new Date(bot.ultimo_conectado_em).toLocaleString('pt-BR')}
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg flex items-center gap-3">
                    <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-sm text-blue-700 dark:text-blue-400">Aguardando conexão...</span>
                  </div>
                )}

                {bot.status === 'active' && (
                  <button
                    onClick={async () => {
                      setWaLoading(true)
                      try {
                        await whatsappService.logout(bot.nome)
                        await botsService.pause(bot.id)
                        await fetchBots()
                      } catch (err: any) {
                        setWaError(err?.response?.data?.message || 'Erro ao desconectar')
                      } finally {
                        setWaLoading(false)
                      }
                    }}
                    disabled={waLoading}
                    className="px-4 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm font-medium disabled:opacity-50 flex items-center gap-2"
                  >
                    {waLoading ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : null}
                    Desconectar
                  </button>
                )}
              </div>
            )}

            {/* Disconnected / Error state - reconnect */}
            {bot && (bot.status === 'disconnected' || bot.status === 'error') && (
              <div className="space-y-4">
                {waError && (
                  <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
                    <p className="text-sm text-red-600 dark:text-red-400">{waError}</p>
                  </div>
                )}

                {waSuccess && (
                  <div className="p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg">
                    <p className="text-sm text-green-600 dark:text-green-400 font-medium">✅ Conectado com sucesso! Redirecionando...</p>
                  </div>
                )}

                {waStatus === 'idle' && !waSuccess && (
                  <>
                    {/* Method selection */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        Método de reconexão
                      </label>
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          type="button"
                          onClick={() => setWaMethod('qrcode')}
                          className={`p-4 rounded-xl border-2 transition ${
                            waMethod === 'qrcode'
                              ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                              : 'border-gray-200 dark:border-gray-600 hover:border-purple-300 dark:hover:border-purple-700'
                          }`}
                        >
                          <div className="flex items-center justify-center gap-2 mb-1">
                            <span className="text-lg">📷</span>
                            <span className="font-medium text-gray-700 dark:text-gray-300 text-sm">QR Code</span>
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400">Escaneie o código</p>
                        </button>

                        <button
                          type="button"
                          onClick={() => setWaMethod('phone')}
                          className={`p-4 rounded-xl border-2 transition ${
                            waMethod === 'phone'
                              ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                              : 'border-gray-200 dark:border-gray-600 hover:border-purple-300 dark:hover:border-purple-700'
                          }`}
                        >
                          <div className="flex items-center justify-center gap-2 mb-1">
                            <span className="text-lg">📱</span>
                            <span className="font-medium text-gray-700 dark:text-gray-300 text-sm">Telefone</span>
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400">Use seu número</p>
                        </button>
                      </div>
                    </div>

                    {/* Phone number input */}
                    {waMethod === 'phone' && (
                      <div>
                        <label htmlFor="waPhone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Seu número WhatsApp
                        </label>
                        <div className="flex">
                          <span className="inline-flex items-center px-3 bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300 text-sm border border-r-0 border-gray-300 dark:border-gray-600 rounded-l-lg">
                            +55
                          </span>
                          <input
                            type="tel"
                            id="waPhone"
                            value={waPhone.replace(/\D/g, '').replace(/^(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3')}
                            onChange={(e) => setWaPhone(e.target.value.replace(/\D/g, ''))}
                            maxLength={16}
                            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-r-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                            placeholder="(11) 99999-9999"
                          />
                        </div>
                      </div>
                    )}

                    {/* Connect button */}
                    <button
                      onClick={async () => {
                        setWaError('')
                        setWaLoading(true)
                        try {
                          const result = await whatsappService.connectWithQRCode({
                            name: bot.nome,
                            qrcode: true,
                          })
                          if (result.qrcode) {
                            setWaQrCode(result.qrcode)
                            setWaStatus('qrcode')
                            startWaStatusPoll(bot.nome, bot.id)
                          } else if (result.status === ConnectionStatus.CONNECTED) {
                            await botsService.resume(bot.id)
                            await fetchBots()
                            setWaStatus('connected')
                            setWaSuccess(true)
                            setTimeout(() => navigate('/dashboard'), 2000)
                          }
                        } catch (err: any) {
                          setWaError(err?.response?.data?.error?.message || 'Erro ao conectar. Tente novamente.')
                        } finally {
                          setWaLoading(false)
                        }
                      }}
                      disabled={waLoading}
                      className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {waLoading ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      ) : null}
                      Conectar via QR Code
                    </button>
                  </>
                )}

                {/* QR Code display */}
                {waStatus === 'qrcode' && waQrCode && (
                  <div className="text-center">
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Escaneie o QR Code</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      Abra o WhatsApp no celular e escaneie o código
                    </p>
                    <div className="inline-block p-4 bg-white rounded-xl shadow-lg border border-gray-200 dark:border-gray-600 mb-4">
                      <img src={`data:image/png;base64,${waQrCode}`} alt="QR Code" className="w-56 h-56" />
                    </div>
                    <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      Aguardando conexão...
                      <span className={`ml-2 font-mono ${waTimeLeft <= 30 ? 'text-red-500 font-bold' : ''}`}>
                        {Math.floor(waTimeLeft / 60)}:{(waTimeLeft % 60).toString().padStart(2, '0')}
                      </span>
                    </div>
                    <button
                      onClick={handleWaReset}
                      className="mt-4 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 underline"
                    >
                      Cancelar
                    </button>
                  </div>
                )}

                {/* Pairing code display */}
                {waStatus === 'pairing' && waPairingCode && (
                  <div className="text-center">
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Digite o código no WhatsApp</h4>
                    <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-4 mb-4">
                      <ol className="text-left text-sm text-gray-700 dark:text-gray-300 space-y-1.5">
                        <li className="flex gap-2"><span className="font-bold text-purple-600 dark:text-purple-400">1.</span> Abra o WhatsApp no celular</li>
                        <li className="flex gap-2"><span className="font-bold text-purple-600 dark:text-purple-400">2.</span> Acesse <strong>Dispositivos conectados</strong></li>
                        <li className="flex gap-2"><span className="font-bold text-purple-600 dark:text-purple-400">3.</span> Toque em <strong>Vincular um telefone</strong></li>
                        <li className="flex gap-2"><span className="font-bold text-purple-600 dark:text-purple-400">4.</span> Digite o código abaixo:</li>
                      </ol>
                    </div>
                    <div className="mb-4 p-4 bg-purple-50 dark:bg-purple-900/30 rounded-xl border border-purple-200 dark:border-purple-700">
                      <p className="text-3xl font-mono font-bold text-purple-700 dark:text-purple-400 tracking-wider">{waPairingCode}</p>
                    </div>
                    <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      Aguardando conexão...
                      <span className={`ml-2 font-mono ${waTimeLeft <= 30 ? 'text-red-500 font-bold' : ''}`}>
                        {Math.floor(waTimeLeft / 60)}:{(waTimeLeft % 60).toString().padStart(2, '0')}
                      </span>
                    </div>
                    <button
                      onClick={handleWaReset}
                      className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 underline"
                    >
                      Cancelar
                    </button>
                  </div>
                )}

                {/* Error state */}
                {waStatus === 'error' && (
                  <div className="text-center">
                    <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg mb-4">
                      <p className="text-sm text-red-600 dark:text-red-400">{waError || 'Erro na conexão'}</p>
                    </div>
                    <button
                      onClick={handleWaReset}
                      className="px-4 py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium"
                    >
                      Tentar novamente
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab: IA (LLM) */}
      {activeTab === 'ia' && (
        <div className="space-y-6">
          {/* Card principal */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 lg:p-6 space-y-6">
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Inteligência Artificial (LLM)</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Ative a IA para respostas inteligentes e automáticas. Escolha o provedor, modelo e personalize o comportamento.
              </p>
            </div>

            {/* Toggle */}
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Ativar respostas com IA</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  O bot usará a IA para gerar respostas personalizadas
                </p>
              </div>
              <button
                onClick={() => setLlmAtivado(!llmAtivado)}
                className={`relative w-12 h-6 rounded-full transition-colors ${llmAtivado ? 'bg-purple-600' : 'bg-gray-300 dark:bg-gray-600'}`}
              >
                <span
                  className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${llmAtivado ? 'translate-x-6' : ''}`}
                />
              </button>
            </div>

            {llmAtivado && (
              <>
                {/* Provider e Modelo */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="llmProvider" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      🏢 Provedor LLM
                    </label>
                    <select
                      id="llmProvider"
                      value={llmProvider}
                      onChange={(e) => {
                        setLlmProvider(e.target.value)
                        // Reset modelo para default do provider
                        const defaults: Record<string, string> = {
                          glm: 'glm-4-flash',
                          openai: 'gpt-4o-mini',
                          anthropic: 'claude-sonnet-4-20250514',
                          ollama: 'llama3',
                        }
                        setLlmModelo(defaults[e.target.value] || 'glm-4-flash')
                      }}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="glm">🇨🇳 GLM (Z.AI) — Padrão</option>
                      <option value="openai">🟢 OpenAI (GPT)</option>
                      <option value="anthropic">🟠 Anthropic (Claude)</option>
                      <option value="ollama">🖥️ Ollama (Local)</option>
                    </select>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      {llmProvider === 'glm' && 'GLM-4 da Z.AI. Rápido e gratuito via API configurada.'}
                      {llmProvider === 'openai' && 'GPT-4o, GPT-4o-mini da OpenAI. Requer API Key.'}
                      {llmProvider === 'anthropic' && 'Claude Sonnet, Claude Haiku da Anthropic. Requer API Key.'}
                      {llmProvider === 'ollama' && 'Modelos locais via Ollama. Requer Ollama rodando em localhost:11434.'}
                    </p>
                  </div>

                  <div>
                    <label htmlFor="llmModelo" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      🤖 Modelo
                    </label>
                    <select
                      id="llmModelo"
                      value={llmModelo}
                      onChange={(e) => setLlmModelo(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      {llmProvider === 'glm' && (
                        <>
                          <option value="glm-4-flash">GLM-4 Flash (rápido)</option>
                          <option value="glm-4">GLM-4 (equilibrado)</option>
                          <option value="glm-4-plus">GLM-4 Plus (preciso)</option>
                          <option value="glm-4-long">GLM-4 Long (grande contexto)</option>
                        </>
                      )}
                      {llmProvider === 'openai' && (
                        <>
                          <option value="gpt-4o-mini">GPT-4o-mini (rápido, econômico)</option>
                          <option value="gpt-4o">GPT-4o (potente)</option>
                          <option value="gpt-4-turbo">GPT-4 Turbo</option>
                          <option value="gpt-3.5-turbo">GPT-3.5 Turbo (legado)</option>
                        </>
                      )}
                      {llmProvider === 'anthropic' && (
                        <>
                          <option value="claude-sonnet-4-20250514">Claude Sonnet 4 (mais recente)</option>
                          <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                          <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku (rápido)</option>
                          <option value="claude-3-haiku-20240307">Claude 3 Haiku (econômico)</option>
                        </>
                      )}
                      {llmProvider === 'ollama' && (
                        <>
                          <option value="llama3">Llama 3</option>
                          <option value="llama3.1">Llama 3.1</option>
                          <option value="mistral">Mistral</option>
                          <option value="gemma2">Gemma 2</option>
                          <option value="phi3">Phi-3</option>
                          <option value="qwen2">Qwen 2</option>
                        </>
                      )}
                    </select>
                  </div>
                </div>

                {/* Temperatura e Max Tokens */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="llmTemperatura" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      🌡️ Temperatura: {llmTemperatura.toFixed(1)}
                    </label>
                    <input
                      id="llmTemperatura"
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={llmTemperatura}
                      onChange={(e) => setLlmTemperatura(parseFloat(e.target.value))}
                      className="w-full mt-2 accent-purple-600"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>Preciso (0.0)</span>
                      <span>Criativo (1.0)</span>
                    </div>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      💡 0.1-0.3 = respostas objetivas. 0.7-1.0 = mais criativas e variadas.
                    </p>
                  </div>

                  <div>
                    <label htmlFor="llmMaxTokens" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      📏 Limite de tokens
                    </label>
                    <select
                      id="llmMaxTokens"
                      value={llmMaxTokens}
                      onChange={(e) => setLlmMaxTokens(parseInt(e.target.value))}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value={512}>512 (curto)</option>
                      <option value={1024}>1024 (médio)</option>
                      <option value={2048}>2048 (padrão)</option>
                      <option value={4096}>4096 (longo)</option>
                    </select>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Tamanho máximo da resposta da IA.
                    </p>
                  </div>
                </div>

                {/* Max Context Messages */}
                <div>
                  <label htmlFor="llmMaxContext" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    💬 Mensagens de contexto
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      id="llmMaxContext"
                      type="range"
                      min="2"
                      max="50"
                      step="2"
                      value={llmMaxContextMessages}
                      onChange={(e) => setLlmMaxContextMessages(parseInt(e.target.value))}
                      className="flex-1 accent-purple-600"
                    />
                    <span className="text-sm font-mono text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 px-3 py-1.5 rounded-lg min-w-[3rem] text-center">
                      {llmMaxContextMessages}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    💡 Quantas mensagens do histórico da conversa enviar para a IA como contexto. Mais mensagens = mais contexto, mas mais tokens consumidos.
                    Estimativa: ~{Math.round(llmMaxContextMessages * 30)} tokens (~{Math.round(llmMaxContextMessages * 120)} chars).
                  </p>
                </div>

                {/* System Prompt */}
                <div>
                  <label htmlFor="llmPrompt" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    🧠 Prompt do Sistema
                  </label>
                  <textarea
                    id="llmPrompt"
                    rows={8}
                    value={llmSystemPrompt}
                    onChange={(e) => setLlmSystemPrompt(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-y font-mono text-sm"
                    placeholder={`Você é um assistente de atendimento ao cliente da empresa XYZ.\n\nRegras:\n- Seja sempre educado e profissional\n- Responda em português brasileiro\n- Se não souber a resposta, diga que vai transferir para um humano\n- Não invente informações sobre preços ou prazos`}
                  />
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    💡 Define a personalidade e comportamento do bot. Quanto mais detalhado, melhores as respostas.
                  </p>
                </div>

                {/* Provider info cards */}
                {llmProvider !== 'glm' && llmProvider !== 'ollama' && (
                  <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <p className="text-sm text-yellow-700 dark:text-yellow-400">
                      🔑 <strong>API Key necessária.</strong> Configure a variável de ambiente{' '}
                      <code className="px-1.5 py-0.5 bg-yellow-100 dark:bg-yellow-800 rounded text-xs">
                        {llmProvider === 'openai' ? 'OPENAI_API_KEY' : 'ANTHROPIC_API_KEY'}
                      </code>{' '}
                      no servidor para usar este provedor.
                    </p>
                  </div>
                )}

                {llmProvider === 'ollama' && (
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <p className="text-sm text-blue-700 dark:text-blue-400">
                      🖥️ <strong>Ollama local.</strong> Certifique-se de que o Ollama está rodando em{' '}
                      <code className="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-800 rounded text-xs">localhost:11434</code>
                      {' '}e que o modelo selecionado está baixado.
                    </p>
                  </div>
                )}
              </>
            )}

            {!llmAtivado && (
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-sm text-yellow-700 dark:text-yellow-400">
                  ⚠️ Com a IA desativada, o bot enviará a <strong>mensagem de resposta padrão</strong> configurada na aba Mensagens.
                </p>
              </div>
            )}
          </div>

          {/* Dicas */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-5">
            <h4 className="font-medium text-blue-900 dark:text-blue-300 mb-2">💡 Dicas para um bom prompt</h4>
            <ul className="text-sm text-blue-800 dark:text-blue-400 space-y-1.5">
              <li>• Defina o <strong>nome da empresa</strong> e o que ela vende/oferece</li>
              <li>• Liste <strong>regras claras</strong> (o que pode e não pode responder)</li>
              <li>• Informe <strong>preços, prazos e políticas</strong> reais</li>
              <li>• Diga o que fazer quando <strong>não souber</strong> a resposta</li>
              <li>• Defina o <strong>tom</strong> (formal, informal, amigável, técnico)</li>
              <li>• Mantenha o prompt <strong>atualizado</strong> com informações recentes</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
