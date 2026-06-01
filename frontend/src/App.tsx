import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import HomePage from './presentation/pages/HomePage'
import LoginPage from './presentation/pages/LoginPage'
import RegisterPage from './presentation/pages/RegisterPage'
import DashboardPage from './presentation/pages/DashboardPage'
import ConfirmEmailPage from './presentation/pages/ConfirmEmailPage'
import ForgotPasswordPage from './presentation/pages/ForgotPasswordPage'
import ResetPasswordPage from './presentation/pages/ResetPasswordPage'
import AddBotPage from './presentation/pages/AddBotPage'
import MainLayout from './presentation/layouts/MainLayout'
import { ProtectedRoute } from './presentation/components/ProtectedRoute'

function PlaceholderPage({ title, description }: { title: string; description: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center mb-4">
        <svg className="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
      </div>
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{title}</h2>
      <p className="text-gray-500 dark:text-gray-400 text-center max-w-md">{description}</p>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/add-bot" element={<AddBotPage />} />
        <Route path="/confirm-email" element={<ConfirmEmailPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
        </Route>

        <Route
          path="/bots"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={
            <div className="space-y-6">
              <PlaceholderPage
                title="Meus Bots"
                description="Gerencie seus bots de WhatsApp e Telegram. Em breve você poderá ver todos os bots conectados aqui."
              />
              <div className="text-center">
                <Link to="/add-bot" className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Adicionar Bot WhatsApp
                </Link>
              </div>
            </div>
          } />
        </Route>

        <Route
          path="/conversations"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<PlaceholderPage title="Conversas" description="Veja todas as conversas dos seus bots em tempo real. Esta funcionalidade estará disponível em breve." />} />
        </Route>

        <Route
          path="/automations"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<PlaceholderPage title="Automações" description="Crie regras de automação, respostas automáticas e fluxos de conversa. Esta funcionalidade estará disponível em breve." />} />
        </Route>

        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<PlaceholderPage title="Analytics" description="Acompanhe métricas de desempenho, volume de mensagens e taxa de resposta dos seus bots. Esta funcionalidade estará disponível em breve." />} />
        </Route>

        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<PlaceholderPage title="Configurações" description="Gerencie suas configurações de conta, perfil e preferências. Esta funcionalidade estará disponível em breve." />} />
        </Route>

        {/* 404 */}
        <Route
          path="*"
          element={
            <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">404</h1>
                <p className="text-gray-600 dark:text-gray-400 mb-8">Página não encontrada</p>
                <a href="/" className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                  Voltar ao início
                </a>
              </div>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
