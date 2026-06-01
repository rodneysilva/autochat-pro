import { useEffect, useState } from 'react'
import { contactsService, type Contato } from '../../infrastructure/api/contacts.service'

export default function ContactsPage() {
  const [contacts, setContacts] = useState<Contato[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null)

  useEffect(() => {
    fetchContacts()
  }, [])

  const fetchContacts = async (searchTerm?: string) => {
    setIsLoading(true)
    setError('')
    try {
      const params: Record<string, any> = {}
      if (searchTerm) params.search = searchTerm
      const result = await contactsService.list(params)
      setContacts(result.data)
    } catch (err: any) {
      setError(err?.response?.data?.erro?.mensagem || 'Erro ao carregar contatos')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = () => {
    fetchContacts(search)
  }

  const handleDelete = async (contactId: string) => {
    try {
      await contactsService.delete(contactId)
      setContacts(prev => prev.filter(c => c.id !== contactId))
    } catch {}
    setShowDeleteConfirm(null)
  }

  const formatPhone = (phone: string) => {
    if (!phone) return '—'
    const digits = phone.replace(/\D/g, '')
    if (digits.length >= 12) {
      return `+${digits.slice(0, 2)} (${digits.slice(2, 4)}) ${digits.slice(4, 9)}-${digits.slice(9, 13)}`
    }
    if (digits.length >= 11) {
      return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7, 11)}`
    }
    return phone
  }

  const formatRelativeTime = (dateStr: string | null) => {
    if (!dateStr) return '—'
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMin = Math.floor(diffMs / 60000)
    const diffHr = Math.floor(diffMs / 3600000)
    const diffDay = Math.floor(diffMs / 86400000)

    if (diffMin < 1) return 'agora'
    if (diffMin < 60) return `${diffMin}min`
    if (diffHr < 24) return `${diffHr}h`
    if (diffDay < 7) return `${diffDay}d`
    return date.toLocaleDateString('pt-BR')
  }

  const tagColor: Record<string, string> = {
    cliente: 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    lead: 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    prospect: 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    vip: 'bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    suporte: 'bg-orange-50 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">👥 Contatos</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {contacts.length > 0
              ? `${contacts.length} contato${contacts.length > 1 ? 's' : ''}`
              : 'Os contatos serão adicionados automaticamente quando clientes mandarem mensagens.'
            }
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Buscar contato por nome..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          />
        </div>
        <button
          onClick={handleSearch}
          className="px-4 py-2.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition font-medium"
        >
          Buscar
        </button>
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

      {/* Lista */}
      {!isLoading && contacts.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          {/* Desktop header */}
          <div className="hidden sm:grid grid-cols-12 gap-4 px-5 py-3 bg-gray-50 dark:bg-gray-700/50 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-200 dark:border-gray-700">
            <div className="col-span-4">Nome</div>
            <div className="col-span-3">Telefone</div>
            <div className="col-span-2">Tags</div>
            <div className="col-span-1">Msgs</div>
            <div className="col-span-1">Última</div>
            <div className="col-span-1"></div>
          </div>

          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {contacts.map(contact => (
              <div key={contact.id} className="grid grid-cols-1 sm:grid-cols-12 gap-2 sm:gap-4 px-5 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
                {/* Nome + avatar */}
                <div className="sm:col-span-4 flex items-center gap-3">
                  <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-purple-600 dark:text-purple-400 font-medium text-xs">
                      {contact.nome ? contact.nome.charAt(0).toUpperCase() : '?'}
                    </span>
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium text-gray-900 dark:text-white truncate text-sm">
                      {contact.nome || 'Sem nome'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 sm:hidden">
                      {formatPhone(contact.telefone)}
                    </p>
                  </div>
                </div>

                {/* Telefone */}
                <div className="hidden sm:flex sm:col-span-3 items-center text-sm text-gray-600 dark:text-gray-300">
                  {formatPhone(contact.telefone)}
                </div>

                {/* Tags */}
                <div className="hidden sm:flex sm:col-span-2 items-center gap-1 flex-wrap">
                  {contact.tags.slice(0, 2).map(tag => (
                    <span
                      key={tag}
                      className={`px-2 py-0.5 text-xs rounded-full ${tagColor[tag] || 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'}`}
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Mensagens */}
                <div className="hidden sm:flex sm:col-span-1 items-center text-sm text-gray-500 dark:text-gray-400">
                  {contact.total_mensagens}
                </div>

                {/* Última mensagem */}
                <div className="hidden sm:flex sm:col-span-1 items-center text-xs text-gray-500 dark:text-gray-400">
                  {formatRelativeTime(contact.ultima_mensagem_em)}
                </div>

                {/* Ações */}
                <div className="hidden sm:flex sm:col-span-1 items-center justify-end gap-1">
                  <button
                    onClick={() => setShowDeleteConfirm(contact.id)}
                    className="p-1.5 text-gray-400 hover:text-red-500 transition"
                    title="Deletar"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>

                {/* Delete confirm mobile */}
                {showDeleteConfirm === contact.id && (
                  <div className="sm:hidden col-span-1 p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <p className="text-xs text-red-600 dark:text-red-400 mb-2">Deletar contato?</p>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleDelete(contact.id)}
                        className="text-xs bg-red-600 text-white px-3 py-1 rounded"
                      >
                        Sim
                      </button>
                      <button
                        onClick={() => setShowDeleteConfirm(null)}
                        className="text-xs border border-gray-300 dark:border-gray-600 px-3 py-1 rounded"
                      >
                        Não
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && contacts.length === 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 lg:p-12 text-center">
          <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Nenhum contato</h2>
          <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
            Os contatos serão adicionados automaticamente quando clientes enviarem mensagens para seus bots.
            Você também pode buscá-los pelo nome depois que forem registrados.
          </p>

          <div className="mt-6 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-left max-w-md mx-auto">
            <h3 className="text-sm font-medium text-purple-700 dark:text-purple-300 mb-2">💡 Como os contatos são adicionados?</h3>
            <ul className="text-xs text-purple-600 dark:text-purple-400 space-y-1">
              <li>• Quando um cliente manda mensagem pela primeira vez</li>
              <li>• Ao responder uma conversa via WhatsApp</li>
              <li>• Tags são aplicadas automaticamente (cliente, lead, vip)</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
