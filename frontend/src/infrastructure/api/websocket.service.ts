/**
 * Serviço WebSocket para atualizações em tempo real.
 *
 * Gerencia conexão WebSocket, auto-reconnect com exponential backoff,
 * e sistema de eventos para notificar componentes.
 */

type EventCallback = (data: any) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private token: string | null = null
  private listeners: Map<string, Set<EventCallback>> = new Map()
  private _isConnected = false
  private _isReconnecting = false
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private reconnectAttempts = 0
  private maxReconnectDelay = 30000
  private pingInterval: ReturnType<typeof setInterval> | null = null
  private manualClose = false

  /** Conecta ao WebSocket usando token JWT. */
  connect(token: string): void {
    this.manualClose = false
    this.token = token
    this._cleanup()
    this._connect()
  }

  /** Força desconexão (sem auto-reconnect). */
  disconnect(): void {
    this.manualClose = true
    this._cleanup()
    this.token = null
    this._isConnected = false
    this._isReconnecting = false
    this.reconnectAttempts = 0
  }

  /** Registra listener para um evento. */
  on(event: string, callback: EventCallback): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  /** Remove listeners de um evento. */
  off(event: string): void {
    this.listeners.delete(event)
  }

  /** Remove listener específico. */
  offEvent(event: string, callback: EventCallback): void {
    this.listeners.get(event)?.delete(callback)
  }

  get isConnected(): boolean {
    return this._isConnected
  }

  get isReconnecting(): boolean {
    return this._isReconnecting
  }

  private _connect(): void {
    if (!this.token) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws?token=${this.token}`

    try {
      this.ws = new WebSocket(wsUrl)
    } catch {
      this._scheduleReconnect()
      return
    }

    this._isReconnecting = false

    this.ws.onopen = () => {
      this._isConnected = true
      this.reconnectAttempts = 0
      this._emit('_connection', { connected: true })
      this._startPing()
    }

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)

        // Responder ping do servidor
        if (msg.event === 'ping') {
          this.ws?.send(JSON.stringify({ action: 'pong' }))
          return
        }

        this._emit(msg.event, msg.data)
      } catch {
        // Ignorar mensagens inválidas
      }
    }

    this.ws.onclose = (event) => {
      this._isConnected = false
      this._stopPing()
      this._emit('_connection', { connected: false, code: event.code })

      if (!this.manualClose && this.token) {
        this._scheduleReconnect()
      }
    }

    this.ws.onerror = () => {
      this._isConnected = false
      // onclose vai ser chamado em seguida
    }
  }

  private _scheduleReconnect(): void {
    if (this.manualClose) return

    this._isReconnecting = true
    this.reconnectAttempts++

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay)
    this._emit('_connection', { connected: false, reconnecting: true, delay })

    this.reconnectTimer = setTimeout(() => {
      this._connect()
    }, delay)
  }

  private _startPing(): void {
    this._stopPing()
    // Enviar ping a cada 25s (servidor envia ping a cada 30s)
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'pong' }))
      }
    }, 25000)
  }

  private _stopPing(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  private _cleanup(): void {
    this._stopPing()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.onopen = null
      this.ws.onmessage = null
      this.ws.onclose = null
      this.ws.onerror = null
      if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close()
      }
      this.ws = null
    }
  }

  private _emit(event: string, data: any): void {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.forEach((cb) => {
        try {
          cb(data)
        } catch (e) {
          console.error(`WebSocketService: erro no handler de "${event}":`, e)
        }
      })
    }
  }
}

export const wsService = new WebSocketService()
