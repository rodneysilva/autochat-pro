/**
 * Provider para configuração do Cliente HTTP.
 *
 * Configura o cliente HTTP com autenticação e refresh token.
 */

import { useEffect } from 'react'
import { useAuthStore } from '../../application/stores'
import { setupHttpClient } from '../../infrastructure/api/http-client'
import { authService } from '../../infrastructure/api/auth.service'

export function HttpClientProvider({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((state) => state.token)
  const logout = useAuthStore((state) => state.logout)

  useEffect(() => {
    // Configurar o cliente HTTP
    setupHttpClient({
      getToken: () => token,
      refreshToken: async () => {
        try {
          const refreshToken = localStorage.getItem('refresh_token')
          if (!refreshToken) return null

          const response = await authService.refreshToken(refreshToken)

          // Atualizar o token no store
          const setAuth = useAuthStore.getState().setAuth
          const user = useAuthStore.getState().user

          if (user) {
            setAuth(user, response.access_token)
          }

          // Salvar novo refresh token
          localStorage.setItem('refresh_token', response.refresh_token)

          return response.access_token
        } catch (error) {
          console.error('Erro ao renovar token:', error)
          // Se falhar, fazer logout
          logout()
          return null
        }
      },
      onUnauthorized: () => {
        logout()
      },
    })
  }, [token, logout])

  return <>{children}</>
}
