import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './presentation/pages/HomePage'
import LoginPage from './presentation/pages/LoginPage'
import RegisterPage from './presentation/pages/RegisterPage'
import DashboardPage from './presentation/pages/DashboardPage'
import ConfirmEmailPage from './presentation/pages/ConfirmEmailPage'
import ForgotPasswordPage from './presentation/pages/ForgotPasswordPage'
import ResetPasswordPage from './presentation/pages/ResetPasswordPage'
import ConfirmPhonePage from './presentation/pages/ConfirmPhonePage'
import MainLayout from './presentation/layouts/MainLayout'
import { ProtectedRoute } from './presentation/components/ProtectedRoute'

// Placeholder pages
function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">{title}</h2>
        <p className="text-gray-500">Página em desenvolvimento</p>
      </div>
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
          path="/confirm-phone"
          element={
            <ProtectedRoute>
              <ConfirmPhonePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/bots"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<PlaceholderPage title="Bots" />} />
        </Route>

        <Route
          path="/conversations"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<PlaceholderPage title="Conversas" />} />
        </Route>

        <Route
          path="/automations"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<PlaceholderPage title="Automações" />} />
        </Route>

        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<PlaceholderPage title="Analytics" />} />
        </Route>

        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<PlaceholderPage title="Configurações" />} />
        </Route>

        {/* 404 */}
        <Route
          path="*"
          element={
            <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                <p className="text-gray-600 mb-8">Página não encontrada</p>
                <a
                  href="/"
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                >
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
