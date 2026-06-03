/**
 * Serviço de Chat LLM.
 *
 * Comunicação com endpoints de chat com IA:
 * - POST /api/v1/chat/complete (resposta completa)
 * - POST /api/v1/chat/stream  (SSE streaming)
 * - GET  /api/v1/chat/providers (lista de providers/modelos)
 */

import { getHttpClient } from './http-client'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  provider?: string
  model?: string
  system_prompt?: string
  temperature?: number
  max_tokens?: number
}

export interface ChatResponse {
  resposta: string
}

export interface ChatProvider {
  name: string
  models: string[]
}

interface ProvidersResponse {
  providers: ChatProvider[]
}

export class ChatService {
  /**
   * Envia mensagens e recebe resposta completa.
   */
  async complete(request: ChatRequest): Promise<ChatResponse> {
    const client = getHttpClient()
    return client.post<ChatResponse>('/chat/complete', request)
  }

  /**
   * Envia mensagens e recebe tokens via SSE streaming.
   *
   * Chama onToken para cada token recebido.
   * Retorna a resposta completa acumulada.
   */
  async stream(
    request: ChatRequest,
    onToken: (token: string) => void,
    signal?: AbortSignal
  ): Promise<string> {
    const client = getHttpClient()
    const token = (client as any).getToken?.() || localStorage.getItem('token')

    const response = await fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(request),
      signal,
    })

    if (!response.ok) {
      const text = await response.text().catch(() => '')
      throw new Error(`Erro ${response.status}: ${text || response.statusText}`)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('Stream não disponível')

    const decoder = new TextDecoder()
    let fullText = ''
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // Processar linhas SSE completas
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // última linha incompleta vai pro buffer

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || trimmed.startsWith(':')) continue // comentário SSE

        if (trimmed.startsWith('data: ')) {
          const data = trimmed.slice(6)

          if (data === '[DONE]') continue

          try {
            // Pode ser JSON com token ou texto puro
            const parsed = JSON.parse(data)
            if (parsed.token) {
              fullText += parsed.token
              onToken(parsed.token)
            } else if (parsed.resposta) {
              fullText += parsed.resposta
              onToken(parsed.resposta)
            } else if (typeof parsed === 'string') {
              fullText += parsed
              onToken(parsed)
            }
          } catch {
            // Texto puro
            fullText += data
            onToken(data)
          }
        }
      }
    }

    return fullText
  }

  /**
   * Lista providers e modelos disponíveis.
   */
  async getProviders(): Promise<ChatProvider[]> {
    const client = getHttpClient()
    const resp = await client.get<ProvidersResponse>('/chat/providers')
    return resp.providers || []
  }
}

export const chatService = new ChatService()
