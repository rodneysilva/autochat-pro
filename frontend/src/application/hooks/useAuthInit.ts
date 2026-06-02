/**
 * Hook de inicialização de autenticação.
 *
 * Verifica a validade do token ao carregar a aplicação.
 * Se o token expirou, tenta refresh. Se refresh falhar, faz logout.
 */

import { useState, useEffect } from 'react'
import { useAuthStore } from '../stores'
import { authService } from '../../infrastructure/api/auth.service'

export function useAuthInit(): { initialized: boolean } {
  const [initialized, setInitialized] = useState(false)
  const token = useAuthStore((state) => state.token)
  const user = useAuthStore((state) => state.user)
  const setAuth = useAuthStore((state) => state.setAuth)
  const logout = useAuthStore((state) => state.logout)

  useEffect(() => {
    let cancelled = false

    async function verifyAuth() {
      // Sem token = não autenticado, pronto
      if (!token) {
        setInitialized(true)
        return
      }

      try {
        // Tentar chamar /auth/me para validar o token
        const me = await authService.getMe()

        if (cancelled) return

        // Token válido — atualizar dados do user
        if (user && me) {
          setAuth(
            {
              id: me.id,
              email: me.email,
              nome: me.nome || me.name || user.nome,
              avatar: me.avatar || user.avatar,
              plano: user.plano, // manter plano do store
            },
            token,
          )
        }

        setInitialized(true)
      } catch {
        if (cancelled) return

        // Token expirado ou inválido — tentar refresh
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          logout()
          setInitialized(true)
          return
        }

        try {
          const response = await authService.refreshToken(refreshToken)
          if (cancelled) return

          // Refresh OK — atualizar store
          if (user) {
            setAuth(user, response.access_token)
          }
          localStorage.setItem('refresh_token', response.refresh_token)

          setInitialized(true)
        } catch {
          if (cancelled) return

          // Refresh falhou — logout
          logout()
          setInitialized(true)
        }
      }
    }

    verifyAuth()

    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return { initialized }
}
