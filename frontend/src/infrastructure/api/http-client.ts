/**
 * Cliente HTTP para comunicação com a API.
 *
 * Implementa um cliente Axios configurado com interceptors
 * para autenticação, tratamento de erros e refresh de token.
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

// URL base da API - usa variável de ambiente ou URL relativa (nginx proxy)
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

/**
 * Tipos de erro da API.
 */
export interface ApiError {
  codigo: string
  mensagem: string
  detalhes?: Record<string, unknown>
}

/**
 * Configuração do cliente HTTP.
 */
interface HttpClientConfig {
  baseURL?: string
  getToken?: () => string | null
  refreshToken?: () => Promise<string | null>
  onUnauthorized?: () => void
}

/**
 * Cliente HTTP configurado para a aplicação.
 *
 * Fornece métodos para requisições HTTP com tratamento automático
 * de autenticação e erros.
 */
export class HttpClient {
  private client: AxiosInstance
  private getToken?: () => string | null
  private refreshToken?: () => Promise<string | null>
  private onUnauthorized?: () => void
  private isRefreshing = false
  private pendingRequests: Array<{ resolve: (token: string) => void; reject: (error: unknown) => void }> = []

  constructor(config: HttpClientConfig = {}) {
    const {
      baseURL = API_BASE_URL,
      getToken,
      refreshToken,
      onUnauthorized,
    } = config

    this.getToken = getToken
    this.refreshToken = refreshToken
    this.onUnauthorized = onUnauthorized

    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  /**
   * Configura os interceptores de requisição e resposta.
   */
  private setupInterceptors(): void {
    // Interceptor de requisição
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken?.()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Interceptor de resposta
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<{ erro: ApiError }>) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & {
          _retry?: boolean
        }

        // Erro 401 - Não autorizado
        if (error.response?.status === 401 && !originalRequest._retry) {
          // Se já está fazendo refresh, enfileirar a request
          if (this.isRefreshing) {
            return new Promise<string>((resolve, reject) => {
              this.pendingRequests.push({ resolve, reject })
            }).then((newToken) => {
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              return this.client(originalRequest)
            })
          }

          originalRequest._retry = true
          this.isRefreshing = true

          try {
            const newToken = await this.refreshToken?.()
            if (newToken) {
              // Resolver requests pendentes com o novo token
              this.pendingRequests.forEach(({ resolve }) => resolve(newToken))
              this.pendingRequests = []

              originalRequest.headers.Authorization = `Bearer ${newToken}`
              return this.client(originalRequest)
            }
          } catch (refreshError) {
            // Rejeitar requests pendentes
            this.pendingRequests.forEach(({ reject }) => reject(refreshError))
            this.pendingRequests = []

            // Refresh falhou — fazer logout
            this.onUnauthorized?.()
            return Promise.reject(refreshError)
          } finally {
            this.isRefreshing = false
          }
        }

        // Se 401 e já tentou refresh (_retry=true), fazer logout
        if (error.response?.status === 401 && originalRequest._retry) {
          this.onUnauthorized?.()
        }

        // Outros erros
        return Promise.reject(this.handleError(error))
      }
    )
  }

  /**
   * Tratamento de erros da API.
   */
  private handleError(error: AxiosError<{ erro: ApiError }>): Error {
    if (error.response?.data?.erro) {
      const apiError = error.response.data.erro
      return new ApiErrorResponse(apiError.codigo, apiError.mensagem, apiError.detalhes)
    }

    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return new Error('Tempo de requisição esgotado')
    }

    if (!navigator.onLine) {
      return new Error('Sem conexão com a internet')
    }

    return new Error('Erro ao comunicar com o servidor')
  }

  /**
   * Requisição GET.
   */
  async get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    const response = await this.client.get<T>(url, { params })
    return response.data
  }

  /**
   * Requisição POST.
   */
  async post<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.post<T>(url, data)
    return response.data
  }

  /**
   * Requisição PUT.
   */
  async put<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.put<T>(url, data)
    return response.data
  }

  /**
   * Requisição PATCH.
   */
  async patch<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.patch<T>(url, data)
    return response.data
  }

  /**
   * Requisição DELETE.
   */
  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url)
    return response.data
  }
}

/**
 * Classe de erro de resposta da API.
 */
export class ApiErrorResponse extends Error {
  constructor(
    public codigo: string,
    mensagem: string,
    public detalhes?: Record<string, unknown>
  ) {
    super(mensagem)
    this.name = 'ApiErrorResponse'
  }
}

// Instância padrão do cliente (será configurada pelo provider)
let defaultClient: HttpClient | null = null

/**
 * Configura o cliente HTTP padrão.
 */
export function setupHttpClient(config: HttpClientConfig): void {
  defaultClient = new HttpClient(config)
}

/**
 * Retorna o cliente HTTP padrão.
 */
export function getHttpClient(): HttpClient {
  if (!defaultClient) {
    defaultClient = new HttpClient()
  }
  return defaultClient
}
