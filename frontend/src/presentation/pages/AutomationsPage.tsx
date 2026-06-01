import { useEffect, useState } from 'react'
import { automationsService, RegraResponse, CondicaoDTO, AcaoDTO } from '../../infrastructure/api/automations.service'
import { botsService } from '../../infrastructure/api/bots.service'

const TIPOS_CONDICAO = [
  { value: 'keyword', label: 'Palavra-chave' },
  { value: 'regex', label: 'Expressão Regular' },
  { value: 'time', label: 'Horário' },
  { value: 'intent', label: 'Intenção' },
  { value: 'has_media', label: 'Tem Mídia' },
]

const OPERADORES = [
  { value: 'contains', label: 'Contém' },
  { value: 'equals', label: 'Igual a' },
  { value: 'starts_with', label: 'Começa com' },
  { value: 'ends_with', label: 'Termina com' },
  { value: 'regex_match', label: 'Regex' },
]

const TIPOS_ACAO = [
  { value: 'reply', label: 'Responder' },
  { value: 'forward', label: 'Encaminhar' },
  { value: 'llm', label: 'Usar IA' },
  { value: 'tag', label: 'Adicionar Tag' },
  { value: 'close', label: 'Fechar Conversa' },
  { value: 'assign_human', label: 'Atribuir Humano' },
]

const condicaoLabel = (c: CondicaoDTO) => {
  const tipo = TIPOS_CONDICAO.find(t => t.value === c.tipo)?.label || c.tipo
  const op = OPERADORES.find(o => o.value === c.operador)?.label || c.operador
  const neg = c.negar ? 'NÃO ' : ''
  return `${neg}${tipo}: ${c.valor || op}`
}

const acaoLabel = (a: AcaoDTO) => {
  const tipo = TIPOS_ACAO.find(t => t.value === a.tipo)?.label || a.tipo
  return a.conteudo ? `${tipo}: "${a.conteudo.substring(0, 40)}"` : tipo
}

export default function AutomationsPage() {
  const [bots, setBots] = useState<{ id: string; nome: string }[]>([])
  const [selectedBotId, setSelectedBotId] = useState('')
  const [rules, setRules] = useState<RegraResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [editingRule, setEditingRule] = useState<RegraResponse | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  // Form state
  const [formNome, setFormNome] = useState('')
  const [formDescricao, setFormDescricao] = useState('')
  const [formPrioridade, setFormPrioridade] = useState(10)
  const [formCooldown, setFormCooldown] = useState(300)
  const [formAtiva, setFormAtiva] = useState(true)
  const [formCondicoes, setFormCondicoes] = useState<CondicaoDTO[]>([])
  const [formAcoes, setFormAcoes] = useState<AcaoDTO[]>([])

  useEffect(() => {
    loadBots()
  }, [])

  useEffect(() => {
    if (selectedBotId) loadRules()
  }, [selectedBotId])

  const loadBots = async () => {
    try {
      const res = await botsService.list()
      setBots(res.data.map(b => ({ id: b.id, nome: b.nome })))
      if (res.data.length > 0 && !selectedBotId) {
        setSelectedBotId(res.data[0].id)
      }
    } catch {}
  }

  const loadRules = async () => {
    if (!selectedBotId) return
    setLoading(true)
    try {
      const res = await automationsService.list(selectedBotId)
      setRules(res.data)
    } catch {}
    setLoading(false)
  }

  const openCreate = () => {
    setEditingRule(null)
    setFormNome('')
    setFormDescricao('')
    setFormPrioridade(10)
    setFormCooldown(300)
    setFormAtiva(true)
    setFormCondicoes([{ tipo: 'keyword', campo: 'message.content', operador: 'contains', valor: '', negar: false }])
    setFormAcoes([{ tipo: 'reply', delay: 0, conteudo: '', parametros: {} }])
    setShowModal(true)
  }

  const openEdit = (rule: RegraResponse) => {
    setEditingRule(rule)
    setFormNome(rule.nome)
    setFormDescricao(rule.descricao)
    setFormPrioridade(rule.prioridade)
    setFormCooldown(rule.cooldown)
    setFormAtiva(rule.ativa)
    setFormCondicoes(rule.condicoes.map(c => ({ ...c })))
    setFormAcoes(rule.acoes.map(a => ({ ...a })))
    setShowModal(true)
  }

  const addCondicao = () => {
    setFormCondicoes([...formCondicoes, { tipo: 'keyword', campo: 'message.content', operador: 'contains', valor: '', negar: false }])
  }

  const removeCondicao = (i: number) => {
    setFormCondicoes(formCondicoes.filter((_, idx) => idx !== i))
  }

  const updateCondicao = (i: number, field: keyof CondicaoDTO, value: string | boolean) => {
    const updated = [...formCondicoes]
    updated[i] = { ...updated[i], [field]: value }
    setFormCondicoes(updated)
  }

  const addAcao = () => {
    setFormAcoes([...formAcoes, { tipo: 'reply', delay: 0, conteudo: '', parametros: {} }])
  }

  const removeAcao = (i: number) => {
    setFormAcoes(formAcoes.filter((_, idx) => idx !== i))
  }

  const updateAcao = (i: number, field: keyof AcaoDTO, value: string | number | Record<string, unknown>) => {
    const updated = [...formAcoes]
    updated[i] = { ...updated[i], [field]: value }
    setFormAcoes(updated)
  }

  const handleSave = async () => {
    if (!formNome.trim() || !selectedBotId) return
    try {
      if (editingRule) {
        await automationsService.update(editingRule.id, {
          nome: formNome,
          descricao: formDescricao,
          prioridade: formPrioridade,
          cooldown_seconds: formCooldown,
          ativa: formAtiva,
          condicoes: formCondicoes,
          acoes: formAcoes,
        })
      } else {
        await automationsService.create({
          bot_id: selectedBotId,
          nome: formNome,
          descricao: formDescricao,
          prioridade: formPrioridade,
          cooldown_seconds: formCooldown,
          ativa: formAtiva,
          condicoes: formCondicoes,
          acoes: formAcoes,
        })
      }
      setShowModal(false)
      loadRules()
    } catch {}
  }

  const handleToggle = async (ruleId: string) => {
    try {
      await automationsService.toggle(ruleId)
      loadRules()
    } catch {}
  }

  const handleDelete = async (ruleId: string) => {
    setDeletingId(ruleId)
    try {
      await automationsService.delete(ruleId)
      loadRules()
    } catch {}
    setDeletingId(null)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">⚡ Automações</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {rules.length > 0
              ? `${rules.length} regra${rules.length > 1 ? 's' : ''} configurada${rules.length > 1 ? 's' : ''}`
              : 'Crie regras para respostas automáticas'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {bots.length > 1 && (
            <select
              value={selectedBotId}
              onChange={(e) => setSelectedBotId(e.target.value)}
              className="px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white"
            >
              {bots.map(b => (
                <option key={b.id} value={b.id}>{b.nome}</option>
              ))}
            </select>
          )}
          {selectedBotId && (
            <button
              onClick={openCreate}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition font-medium"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Nova Regra
            </button>
          )}
        </div>
      </div>

      {/* No bot selected */}
      {!selectedBotId && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
          <div className="text-4xl mb-4">🤖</div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Selecione um bot</h2>
          <p className="text-gray-500 dark:text-gray-400">Crie um bot primeiro para configurar automações.</p>
        </div>
      )}

      {/* Loading */}
      {loading && selectedBotId && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {/* Rules list */}
      {!loading && rules.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {rules.map(rule => (
            <div key={rule.id} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-md transition">
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">{rule.nome}</h3>
                    {rule.descricao && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{rule.descricao}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleToggle(rule.id)}
                    className={`ml-3 flex-shrink-0 relative w-11 h-6 rounded-full transition-colors ${
                      rule.ativa ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  >
                    <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                      rule.ativa ? 'translate-x-5' : ''
                    }`} />
                  </button>
                </div>

                {/* Conditions */}
                <div className="mb-3">
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">SE</p>
                  <div className="flex flex-wrap gap-1">
                    {rule.condicoes.map((c, i) => (
                      <span key={i} className="px-2 py-0.5 text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-full">
                        {i > 0 && 'OU '}
                        {condicaoLabel(c)}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="mb-3">
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">ENTÃO</p>
                  <div className="flex flex-wrap gap-1">
                    {rule.acoes.map((a, i) => (
                      <span key={i} className="px-2 py-0.5 text-xs bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-full">
                        {acaoLabel(a)}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Stats */}
                <div className="flex items-center gap-4 mb-4 text-xs text-gray-500 dark:text-gray-400">
                  <span>Prioridade: <strong className="text-gray-700 dark:text-gray-300">{rule.prioridade}</strong></span>
                  <span>Cooldown: <strong className="text-gray-700 dark:text-gray-300">{rule.cooldown}s</strong></span>
                  <span>Execuções: <strong className="text-gray-700 dark:text-gray-300">{rule.estatisticas.total_execucoes}</strong></span>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => openEdit(rule)}
                    className="flex-1 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium"
                  >
                    ✏️ Editar
                  </button>
                  <button
                    onClick={() => handleDelete(rule.id)}
                    disabled={deletingId === rule.id}
                    className="px-3 py-2 text-sm border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 transition"
                  >
                    {deletingId === rule.id ? '...' : '🗑️'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && selectedBotId && rules.length === 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 lg:p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">⚡</span>
          </div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Nenhuma automação</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">Crie regras para responder automaticamente com base em palavras-chave, horários e mais.</p>
          <button onClick={openCreate} className="inline-flex items-center gap-2 px-4 py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium">
            Criar Primeira Regra
          </button>
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl my-8">
            <div className="p-5 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                {editingRule ? 'Editar Regra' : 'Nova Regra'}
              </h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-xl">✕</button>
            </div>

            <div className="p-5 space-y-5 max-h-[70vh] overflow-y-auto">
              {/* Name & Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nome *</label>
                <input
                  type="text"
                  value={formNome}
                  onChange={e => setFormNome(e.target.value)}
                  className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Ex: Saudação automática"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Descrição</label>
                <input
                  type="text"
                  value={formDescricao}
                  onChange={e => setFormDescricao(e.target.value)}
                  className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Opcional"
                />
              </div>

              {/* Priority & Cooldown */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Prioridade (1-100)</label>
                  <input
                    type="number"
                    min={1} max={100}
                    value={formPrioridade}
                    onChange={e => setFormPrioridade(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Cooldown (segundos)</label>
                  <input
                    type="number"
                    min={0}
                    value={formCooldown}
                    onChange={e => setFormCooldown(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              {/* Active toggle */}
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setFormAtiva(!formAtiva)}
                  className={`relative w-11 h-6 rounded-full transition-colors ${formAtiva ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'}`}
                >
                  <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${formAtiva ? 'translate-x-5' : ''}`} />
                </button>
                <span className="text-sm text-gray-700 dark:text-gray-300">Ativa</span>
              </div>

              {/* Conditions */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Condições (SE)</label>
                  <button onClick={addCondicao} className="text-xs text-purple-600 hover:text-purple-700 font-medium">+ Adicionar</button>
                </div>
                {formCondicoes.map((c, i) => (
                  <div key={i} className="flex items-center gap-2 mb-2">
                    <select
                      value={c.tipo}
                      onChange={e => updateCondicao(i, 'tipo', e.target.value)}
                      className="px-2 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-xs text-gray-900 dark:text-white"
                    >
                      {TIPOS_CONDICAO.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                    <select
                      value={c.operador}
                      onChange={e => updateCondicao(i, 'operador', e.target.value)}
                      className="px-2 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-xs text-gray-900 dark:text-white"
                    >
                      {OPERADORES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                    <input
                      type="text"
                      value={c.valor}
                      onChange={e => updateCondicao(i, 'valor', e.target.value)}
                      className="flex-1 px-2 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-xs text-gray-900 dark:text-white"
                      placeholder="Valor..."
                    />
                    <label className="flex items-center gap-1 text-xs text-gray-500">
                      <input
                        type="checkbox"
                        checked={c.negar}
                        onChange={e => updateCondicao(i, 'negar', e.target.checked)}
                        className="rounded"
                      />
                      Negar
                    </label>
                    {formCondicoes.length > 1 && (
                      <button onClick={() => removeCondicao(i)} className="text-red-400 hover:text-red-600 text-xs">✕</button>
                    )}
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Ações (ENTÃO)</label>
                  <button onClick={addAcao} className="text-xs text-purple-600 hover:text-purple-700 font-medium">+ Adicionar</button>
                </div>
                {formAcoes.map((a, i) => (
                  <div key={i} className="flex items-start gap-2 mb-2">
                    <select
                      value={a.tipo}
                      onChange={e => updateAcao(i, 'tipo', e.target.value)}
                      className="px-2 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-xs text-gray-900 dark:text-white"
                    >
                      {TIPOS_ACAO.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                    {a.tipo === 'reply' && (
                      <input
                        type="text"
                        value={a.conteudo}
                        onChange={e => updateAcao(i, 'conteudo', e.target.value)}
                        className="flex-1 px-2 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-xs text-gray-900 dark:text-white"
                        placeholder="Texto da resposta... Use {nome} para personalizar"
                      />
                    )}
                    {a.tipo === 'forward' && (
                      <input
                        type="text"
                        value={(a.parametros.phone as string) || ''}
                        onChange={e => updateAcao(i, 'parametros', { ...a.parametros, phone: e.target.value })}
                        className="flex-1 px-2 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-xs text-gray-900 dark:text-white"
                        placeholder="Número para encaminhar..."
                      />
                    )}
                    {a.tipo === 'tag' && (
                      <input
                        type="text"
                        value={a.conteudo}
                        onChange={e => updateAcao(i, 'conteudo', e.target.value)}
                        className="flex-1 px-2 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-xs text-gray-900 dark:text-white"
                        placeholder="Nome da tag..."
                      />
                    )}
                    {(a.tipo === 'llm' || a.tipo === 'close' || a.tipo === 'assign_human') && (
                      <span className="flex-1 py-1.5 text-xs text-gray-500 dark:text-gray-400">Sem parâmetros adicionais</span>
                    )}
                    {formAcoes.length > 1 && (
                      <button onClick={() => removeAcao(i)} className="text-red-400 hover:text-red-600 text-xs mt-1.5">✕</button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="p-5 border-t border-gray-200 dark:border-gray-700 flex items-center gap-3 justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                disabled={!formNome.trim() || formCondicoes.length === 0 || formAcoes.length === 0}
                className="px-4 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium disabled:opacity-50"
              >
                {editingRule ? 'Salvar' : 'Criar Regra'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
