import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { botsService } from '../../infrastructure/api/bots.service'
import { useBotsStore } from '../../application/stores/botsStore'

type Tab = 'mensagens' | 'horario' | 'ia'

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
  const [llmModelo, setLlmModelo] = useState('glm-4-flash')
  const [llmTemperatura, setLlmTemperatura] = useState(0.7)
  const [llmMaxTokens, setLlmMaxTokens] = useState(2048)
  const [llmSystemPrompt, setLlmSystemPrompt] = useState('')

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
      setLlmModelo(bot.llm_config?.modelo || 'glm-4-flash')
      setLlmTemperatura(bot.llm_config?.temperatura ?? 0.7)
      setLlmMaxTokens(bot.llm_config?.max_tokens || 2048)
      setLlmSystemPrompt(bot.llm_config?.system_prompt || '')

      setLoading(false)
    }
  }, [bot, botId, bots.length])

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
        data.llm_modelo = llmModelo
        data.llm_temperatura = llmTemperatura
        data.llm_max_tokens = llmMaxTokens
        data.llm_system_prompt = llmSystemPrompt
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
    { key: 'ia', label: 'IA (GLM)', icon: '⚡' },
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

      {/* Tab: IA (GLM) */}
      {activeTab === 'ia' && (
        <div className="space-y-6">
          {/* Card principal */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 lg:p-6 space-y-6">
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Inteligência Artificial (GLM)</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Ative a IA GLM para respostas inteligentes e automáticas. O bot usará seu prompt de sistema para entender o contexto e responder aos clientes.
              </p>
            </div>

            {/* Toggle */}
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Ativar respostas com IA</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  O bot usará a IA GLM para gerar respostas personalizadas
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
                    💡 Este prompt define a personalidade e o comportamento do bot. Quanto mais detalhado, melhores as respostas.
                  </p>
                  <details className="mt-2">
                    <summary className="text-xs text-purple-600 dark:text-purple-400 cursor-pointer hover:underline">
                      Ver exemplos de prompt
                    </summary>
                    <div className="mt-2 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-xs text-gray-600 dark:text-gray-400 space-y-3">
                      <div>
                        <p className="font-medium text-purple-700 dark:text-purple-300">🛒 E-commerce</p>
                        <pre className="mt-1 whitespace-pre-wrap">{`Você é um assistente de atendimento da Loja XYZ, uma loja de eletrônicos online.

Regras:
- Seja amigável e prestativo
- Responda sobre produtos, preços e prazos de entrega
- Prazo padrão: 3-7 dias úteis para SP, 7-15 para outras capitais
- Frete grátis acima de R$ 299
- Trocas em até 30 dias com produto em perfeitas condições
- Se o cliente pedir para falar com humano, diga que vai transferir
- Não invente preços — se não souber, pergunte qual produto`}</pre>
                      </div>
                      <div>
                        <p className="font-medium text-purple-700 dark:text-purple-300">🍕 Restaurante</p>
                        <pre className="mt-1 whitespace-pre-wrap">{`Você é o assistente virtual do Restaurante ABC, especializado em comida italiana.

Regras:
- Funcionamos de terça a domingo, 11h às 22h
- Cardápio especial: pizzas a partir de R$ 35, massas a partir de R$ 28
- Aceitamos PIX, cartão e dinheiro na entrega
- Taxa de entrega: R$ 8 (até 5km), R$ 12 (5-10km)
- Tempo de entrega: 30-50 minutos
- Se o cliente quiser reservar mesa, peça nome, telefone e data/hora`}</pre>
                      </div>
                    </div>
                  </details>
                </div>

                {/* Modelo e parâmetros */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label htmlFor="llmModelo" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Modelo
                    </label>
                    <select
                      id="llmModelo"
                      value={llmModelo}
                      onChange={(e) => setLlmModelo(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="glm-4-flash">GLM-4 Flash (rápido)</option>
                      <option value="glm-4">GLM-4 (equilibrado)</option>
                      <option value="glm-4-plus">GLM-4 Plus (preciso)</option>
                    </select>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Flash = respostas mais rápidas. Plus = mais preciso.
                    </p>
                  </div>

                  <div>
                    <label htmlFor="llmTemperatura" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Temperatura: {llmTemperatura.toFixed(1)}
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
                      <span>Preciso</span>
                      <span>Criativo</span>
                    </div>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      💡 0.1-0.3 = respostas objetivas. 0.7-1.0 = respostas mais criativas e variadas.
                    </p>
                  </div>

                  <div>
                    <label htmlFor="llmMaxTokens" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Limite de tokens
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
              </>
            )}

            {!llmAtivado && (
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-sm text-yellow-700 dark:text-yellow-400">
                  ⚠️ Com a IA desativada, o bot enviará a <strong>mensagem de resposta padrão</strong> configurada na aba Mensagens para todas as interações.
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
