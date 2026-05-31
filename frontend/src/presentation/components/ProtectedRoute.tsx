/**
 * Componente de rota protegida.
 *
 * Protege rotas que requerem autenticação, redirecionando
 * usuários não autenticados para a página de login.
 */

import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../../application/stores'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
