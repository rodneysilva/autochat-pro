import { useState, useRef, useEffect, useCallback } from 'react'
import { useAuthStore } from '../../application/stores'
import { chatService, type ChatMessage } from '../../infrastructure/api/chat.service'

const MODELS = [
  { value: 'glm-4.5-air', label: 'GLM 4.5 Air', desc: 'Rápido e leve' },
  { value: 'glm-4.5', label: 'GLM 4.5', desc: 'Equilibrado' },
  { value: 'glm-5', label: 'GLM 5', desc: 'Poderoso' },
  { value: 'glm-5-turbo', label: 'GLM 5 Turbo', desc: 'Ultra rápido' },
]

const DEFAULT_SYSTEM_PROMPT = 'Você é um assistente inteligente e prestativo. Responda em português brasileiro de forma clara e concisa.'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatPage() {
  const token = useAuthStore((s) => s.token)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [selectedModel, setSelectedModel] = useState('glm-4.5-air')
  const [systemPrompt, setSystemPrompt] = useState(DEFAULT_SYSTEM_PROMPT)
  const [showSystemPrompt, setShowSystemPrompt] = useState(false)
  const [error, setError] = useState('')

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingContent, scrollToBottom])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || isStreaming) return

    setError('')
    setInput('')

    const userMsg: Message = { role: 'user', content: text }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setIsStreaming(true)
    setStreamingContent('')

    const chatMessages: ChatMessage[] = newMessages.map((m) => ({
      role: m.role,
      content: m.content,
    }))

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const fullResponse = await chatService.stream(
        {
          messages: chatMessages,
          provider: 'glm',
          model: selectedModel,
          system_prompt: systemPrompt,
          temperature: 0.7,
          max_tokens: 2048,
        },
        (token) => {
          setStreamingContent((prev) => prev + token)
        },
        controller.signal
      )

      setMessages((prev) => [...prev, { role: 'assistant', content: fullResponse }])
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setError(err.message || 'Erro ao enviar mensagem')
      }
    } finally {
      setIsStreaming(false)
      setStreamingContent('')
      abortRef.current = null
      inputRef.current?.focus()
    }
  }

  const handleStop = () => {
    abortRef.current?.abort()
  }

  const handleClear = () => {
    setMessages([])
    setStreamingContent('')
    setError('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!token) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-gray-500">Faça login para usar o chat.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] lg:h-[calc(100vh-10rem)] max-w-2xl mx-auto w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 px-1">
        <div className="flex items-center gap-2">
          <span className="text-xl">🤖</span>
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Assistente IA</h2>
          {isStreaming && (
            <span className="flex items-center gap-1.5 text-xs text-purple-400">
              <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
              Gerando...
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Model Selector */}
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={isStreaming}
            className="text-xs bg-gray-100 dark:bg-gray-700 border-0 rounded-lg px-2.5 py-1.5 text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-purple-500 cursor-pointer disabled:opacity-50"
          >
            {MODELS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>

          {/* System Prompt Toggle */}
          <button
            onClick={() => setShowSystemPrompt(!showSystemPrompt)}
            className="p-1.5 text-gray-400 hover:text-purple-400 transition rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            title="System Prompt"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>

          {/* Clear */}
          {messages.length > 0 && (
            <button
              onClick={handleClear}
              disabled={isStreaming}
              className="p-1.5 text-gray-400 hover:text-red-400 transition rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
              title="Limpar conversa"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* System Prompt Collapsible */}
      {showSystemPrompt && (
        <div className="mb-3 px-1">
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">System Prompt</label>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            disabled={isStreaming}
            rows={2}
            className="w-full text-sm bg-gray-100 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none disabled:opacity-50"
          />
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 px-1 py-2 scrollbar-thin">
        {messages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center mb-4">
              <span className="text-3xl">💬</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">Assistente IA</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 max-w-xs">
              Envie uma mensagem para começar uma conversa com a inteligência artificial.
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
              Modelo: {MODELS.find((m) => m.value === selectedModel)?.label || selectedModel}
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-2.5 ${
                msg.role === 'user'
                  ? 'bg-purple-600 text-white rounded-br-md'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-md'
              }`}
            >
              <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">{msg.content}</div>
            </div>
          </div>
        ))}

        {/* Streaming message */}
        {isStreaming && streamingContent && (
          <div className="flex justify-start">
            <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-bl-md px-4 py-2.5 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100">
              <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
                {streamingContent}
                <span className="inline-block w-1.5 h-4 bg-purple-500 ml-0.5 animate-pulse rounded-sm" />
              </div>
            </div>
          </div>
        )}

        {/* Streaming loading indicator */}
        {isStreaming && !streamingContent && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-md px-4 py-3 bg-gray-200 dark:bg-gray-700">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex justify-center">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-4 py-2 text-red-600 dark:text-red-400 text-sm max-w-xs">
              {error}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="mt-3 px-1 pb-1">
        <div className="flex items-end gap-2 bg-gray-100 dark:bg-gray-700/50 rounded-2xl px-3 py-2 border border-gray-200 dark:border-gray-600 focus-within:ring-2 focus-within:ring-purple-500 focus-within:border-transparent transition">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Digite sua mensagem..."
            disabled={isStreaming}
            rows={1}
            className="flex-1 bg-transparent resize-none text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 outline-none disabled:opacity-50 max-h-32"
            style={{ minHeight: '24px' }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement
              target.style.height = '24px'
              target.style.height = Math.min(target.scrollHeight, 128) + 'px'
            }}
          />
          {isStreaming ? (
            <button
              onClick={handleStop}
              className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-xl transition flex-shrink-0"
              title="Parar"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="1" />
              </svg>
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="p-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl transition flex-shrink-0 disabled:opacity-40 disabled:cursor-not-allowed"
              title="Enviar"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>
        <p className="text-center text-[10px] text-gray-400 dark:text-gray-500 mt-1.5">
          {MODELS.find((m) => m.value === selectedModel)?.label} · Powered by AutoChat
        </p>
      </div>
    </div>
  )
}
