/**
 * Serviço de autenticação.
 *
 * Comunica com a API de autenticação para registro, login e refresh de tokens.
 */

import { getHttpClient } from './http-client'

export interface RegisterData {
  email: string
  phone?: string
  password: string
  name: string
}

export interface LoginData {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface LoginResponse extends AuthResponse {
  message: string
  user: {
    id: string
    email: string
    nome?: string
    name?: string
    phone?: string
    avatar?: string
    email_confirmed: boolean
    phone_confirmed: boolean
    plano_tipo: string
    plano_max_bots: number
    created_at: string
  }
}

export interface RegisterResponse {
  message: string
  user: {
    id: string
    email: string
    nome?: string
    name?: string
    phone?: string
    avatar?: string
    email_confirmed: boolean
    phone_confirmed: boolean
    plano_tipo: string
    plano_max_bots: number
    created_at: string
  }
}

const AUTH_PATH = '/auth'

export const authService = {
  /**
   * Registra um novo usuário.
   */
  async register(data: RegisterData): Promise<RegisterResponse> {
    const client = getHttpClient()
    return client.post<RegisterResponse>(`${AUTH_PATH}/register`, data)
  },

  /**
   * Realiza login.
   */
  async login(data: LoginData): Promise<LoginResponse> {
    const client = getHttpClient()
    return client.post<LoginResponse>(`${AUTH_PATH}/login`, data)
  },

  /**
   * Renova o token de acesso.
   */
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const client = getHttpClient()
    return client.post<AuthResponse>(`${AUTH_PATH}/refresh`, {
      refresh_token: refreshToken,
    })
  },

  /**
   * Realiza logout.
   */
  async logout(): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.post<{ message: string }>(`${AUTH_PATH}/logout`)
  },

  /**
   * Obtém dados do usuário autenticado.
   */
  async getMe(): Promise<{
    id: string
    email: string
    nome?: string
    name?: string
    phone?: string
    avatar?: string
    email_confirmed: boolean
    phone_confirmed: boolean
    plano_tipo: string
    plano_max_bots: number
    criado_em?: string
    created_at?: string
  }> {
    const client = getHttpClient()
    return client.get(`${AUTH_PATH}/me`)
  },

  /**
   * Confirma email do usuário.
   */
  async confirmEmail(token: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.post<{ message: string }>(`${AUTH_PATH}/confirm-email`, { token })
  },

  /**
   * Reenvia email de confirmação.
   */
  async resendConfirmation(email: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.post<{ message: string }>(`${AUTH_PATH}/resend-confirmation`, { email })
  },

  /**
   * Solicita recuperação de senha.
   */
  async forgotPassword(email: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.post<{ message: string }>(`${AUTH_PATH}/forgot-password`, { email })
  },

  /**
   * Reseta senha com token.
   */
  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.post<{ message: string }>(`${AUTH_PATH}/reset-password`, {
      token,
      new_password: newPassword,
    })
  },

  /**
   * Envia código de verificação por SMS.
   */
  async sendPhoneCode(phone: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.post<{ message: string }>(`${AUTH_PATH}/send-phone-code`, { phone })
  },

  /**
   * Verifica código SMS.
   */
  async verifyPhone(phone: string, code: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.post<{ message: string }>(`${AUTH_PATH}/verify-phone`, { phone, code })
  },
}
