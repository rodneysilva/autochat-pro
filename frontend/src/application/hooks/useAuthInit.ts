/**
 * Hook de inicialização de autenticação.
 *
 * AGUARDA o Zustand persist hydratar do localStorage ANTES de decidir
 * se o usuário está autenticado. Sem isso, o primeiro render vê
 * token=null (estado inicial) e redireciona pro login mesmo tendo
 * token salvo no localStorage.
 */

import { useState, useEffect, useRef } from 'react'
import { useAuthStore } from '../stores'
import { authService } from '../../infrastructure/api/auth.service'

export function useAuthInit(): { initialized: boolean } {
  const [initialized, setInitialized] = useState(false)
  const setAuth = useAuthStore((state) => state.setAuth)
  const logout = useAuthStore((state) => state.logout)
  const hasRun = useRef(false)

  useEffect(() => {
    if (hasRun.current) return
    hasRun.current = true

    let cancelled = false

    async function verifyAuth() {
      // Ler estado JÁ hidratado do store (não do render)
      const { token, user } = useAuthStore.getState()

      // Sem token = não autenticado, pronto
      if (!token) {
        setInitialized(true)
        return
      }

      try {
        const me = await authService.getMe()
        if (cancelled) return

        if (user && me) {
          setAuth(
            {
              id: me.id,
              email: me.email,
              nome: me.nome || me.name || user.nome,
              avatar: me.avatar || user.avatar,
              plano: user.plano,
            },
            token,
          )
        }
        setInitialized(true)
      } catch {
        if (cancelled) return

        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          logout()
          setInitialized(true)
          return
        }

        try {
          const response = await authService.refreshToken(refreshToken)
          if (cancelled) return

          const currentUser = useAuthStore.getState().user
          if (currentUser) {
            setAuth(currentUser, response.access_token)
          }
          localStorage.setItem('refresh_token', response.refresh_token)
          setInitialized(true)
        } catch {
          if (cancelled) return
          logout()
          setInitialized(true)
        }
      }
    }

    function run() {
      if (useAuthStore.persist.hasHydrated()) {
        verifyAuth()
      } else {
        // Aguardar hydration terminar
        const unsub = useAuthStore.persist.onFinishHydration(() => {
          unsub()
          verifyAuth()
        })
      }
    }

    run()
    return () => { cancelled = true }
  }, [])

  return { initialized }
}
