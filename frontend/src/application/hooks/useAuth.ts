/**
 * Hook de autenticação.
 *
 * Fornece funções para login, registro, logout e gerenciamento
 * do estado de autenticação.
 */

import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores'
import { authService } from '../../infrastructure/api/auth.service'

export interface RegisterData {
  email: string
  password: string
  name: string
  phone?: string
}

export interface AuthResult {
  success: boolean
  error?: string
}

export function useAuth() {
  const navigate = useNavigate()
  const { setAuth, logout: storeLogout, setLoading } = useAuthStore()

  /**
   * Registra um novo usuário.
   */
  const register = useCallback(
    async (data: RegisterData): Promise<AuthResult> => {
      try {
        setLoading(true)
        const registerResponse = await authService.register(data)

        // Após registro, fazer login automático
        const loginResponse = await authService.login({
          email: data.email,
          password: data.password,
        })

        setAuth(
          {
            id: loginResponse.user.id,
            email: loginResponse.user.email,
            nome: loginResponse.user.nome || loginResponse.user.name,
            avatar: loginResponse.user.avatar,
            plano: {
              tipo: loginResponse.user.plano_tipo as 'free' | 'basic' | 'pro',
              maxBots: loginResponse.user.plano_max_bots,
              maxMessagesPerMonth: 1000, // TODO: obter da API
              expiresAt: null,
            },
          },
          loginResponse.access_token
        )

        // Salvar refresh token
        localStorage.setItem('refresh_token', loginResponse.refresh_token)

        navigate('/dashboard')
        return { success: true }
      } catch (error: any) {
        console.error('Erro no registro:', error)
        return {
          success: false,
          error: error.response?.data?.erro?.mensagem || error.message || 'Erro ao registrar usuário',
        }
      } finally {
        setLoading(false)
      }
    },
    [setAuth, setLoading, navigate]
  )

  /**
   * Realiza login.
   */
  const login = useCallback(
    async (email: string, password: string): Promise<AuthResult> => {
      try {
        setLoading(true)
        const response = await authService.login({ email, password })

        setAuth(
          {
            id: response.user.id,
            email: response.user.email,
            nome: response.user.nome || response.user.name,
            avatar: response.user.avatar,
            plano: {
              tipo: response.user.plano_tipo as 'free' | 'basic' | 'pro',
              maxBots: response.user.plano_max_bots,
              maxMessagesPerMonth: 1000,
              expiresAt: null,
            },
          },
          response.access_token
        )

        localStorage.setItem('refresh_token', response.refresh_token)

        navigate('/dashboard')
        return { success: true }
      } catch (error: any) {
        console.error('Erro no login:', error)
        return {
          success: false,
          error: error.response?.data?.erro?.mensagem || error.message || 'Email ou senha incorretos',
        }
      } finally {
        setLoading(false)
      }
    },
    [setAuth, setLoading, navigate]
  )

  /**
   * Realiza logout.
   */
  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Erro no logout:', error)
    } finally {
      storeLogout()
      localStorage.removeItem('refresh_token')
      navigate('/login')
    }
  }, [storeLogout, navigate])

  /**
   * Verifica se o usuário está autenticado.
   */
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  /**
   * Obtém o usuário atual.
   */
  const user = useAuthStore((state) => state.user)

  /**
   * Estado de carregamento.
   */
  const isLoading = useAuthStore((state) => state.isLoading)

  return {
    register,
    login,
    logout,
    isAuthenticated,
    user,
    isLoading,
  }
}
