import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../application/hooks/useAuth'
import { ThemeToggle } from '../components/ui/ThemeToggle'

export default function HomePage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const { login, isLoading } = useAuth()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    const result = await login(email, password)
    if (!result.success) {
      setError(result.error || 'Erro ao fazer login')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="w-full px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center shadow">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white">AutoChat Pro</span>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Link to="/register" className="text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 font-medium">
              Criar conta
            </Link>
          </div>
        </div>
      </header>

      {/* Hero + Login */}
      <section className="max-w-7xl mx-auto px-6 py-12 lg:py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left - Info */}
          <div>
            <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Automatize seu atendimento com{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">
                Inteligência Artificial
              </span>
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
              Conecte WhatsApp e Telegram com bots inteligentes. Automatize respostas, gerencie conversas e aumente suas vendas com IA.
            </p>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="text-center p-4 bg-white/60 dark:bg-gray-800/60 rounded-xl backdrop-blur">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">99.9%</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Uptime</div>
              </div>
              <div className="text-center p-4 bg-white/60 dark:bg-gray-800/60 rounded-xl backdrop-blur">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">50ms</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Resposta IA</div>
              </div>
              <div className="text-center p-4 bg-white/60 dark:bg-gray-800/60 rounded-xl backdrop-blur">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">24/7</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Atendimento</div>
              </div>
            </div>

            {/* Tech stack */}
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 text-xs bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 rounded-full font-medium">WhatsApp</span>
              <span className="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 rounded-full font-medium">Telegram</span>
              <span className="px-3 py-1 text-xs bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-400 rounded-full font-medium">IA GLM</span>
              <span className="px-3 py-1 text-xs bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-400 rounded-full font-medium">FastAPI</span>
              <span className="px-3 py-1 text-xs bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-400 rounded-full font-medium">React</span>
              <span className="px-3 py-1 text-xs bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 rounded-full font-medium">MongoDB</span>
            </div>
          </div>

          {/* Right - Login Card */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Bem-vindo de volta</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Entre na sua conta para continuar</p>

            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <div className="p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                </div>
              )}

              <div>
                <label htmlFor="home-email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Email
                </label>
                <input
                  type="email"
                  id="home-email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                  placeholder="seu@email.com"
                />
              </div>

              <div>
                <label htmlFor="home-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Senha
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="home-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                    required
                    className="w-full px-4 py-2.5 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    {showPassword ? (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <Link to="/forgot-password" className="text-xs text-purple-600 dark:text-purple-400 hover:text-purple-700">
                  Esqueci minha senha
                </Link>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Entrando...
                  </span>
                ) : 'Entrar'}
              </button>
            </form>

            <div className="mt-4 text-center">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Não tem conta?{' '}
                <Link to="/register" className="text-purple-600 dark:text-purple-400 hover:text-purple-700 font-medium">
                  Criar conta grátis
                </Link>
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-4">
          Tudo que você precisa para automatizar
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
          Recursos poderosos para transformar seu atendimento em uma máquina de vendas e suporte.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Feature 1 */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm hover:shadow-md transition border border-gray-100 dark:border-gray-700">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/40 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.548-.548-.237 0 0-.579-.657-.853-.967-.273-.31-.548-.099-.548-.099.452-.198.922-.361 1.386-.498.198-.039.374-.058.548-.058.297 0 .688.099 1.097.297.498.298.907.696 1.236 1.097.249.298.548.597.896.696.298.099.548.199.847.199.846 0 .498-.058.946-.199 1.385-.597.946-.498 1.674-1.028 2.266-1.526.498-.498.896-1.196 1.326-1.993.696-.996 1.326-2.07 1.526-3.23.199-1.195-.199-2.664-.598-4.229-1.595-2.364-1.395-4.229-3.529-5.324-6.386-.996-2.763-.696-5.524.498-7.884 1.096-2.363 3.628-3.829 6.384-4.328 2.762-.498 5.523.199 7.885.696 1.196.498 2.364 1.595 3.23 2.991.996 1.396 1.495 3.062 1.595 5.229 0 2.164-.598 3.829-1.595 4.924-.997 1.096-2.564 1.595-4.924 1.595-.498 0-.996-.05-1.495-.149-.498-.099-.996-.248-1.495-.397l-.996 1.495z"/>
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">WhatsApp Business</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Conecte via QR Code ou número de telefone. Gerencie múltiplas instâncias simultaneamente.</p>
          </div>

          {/* Feature 2 */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm hover:shadow-md transition border border-gray-100 dark:border-gray-700">
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/40 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Inteligência Artificial</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Powered by GLM. Respostas inteligentes e contextualizadas para seu negócio em tempo real.</p>
          </div>

          {/* Feature 3 */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm hover:shadow-md transition border border-gray-100 dark:border-gray-700">
            <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/40 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Automações</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Crie regras de automação, fluxos de conversa e respostas automáticas personalizadas.</p>
          </div>

          {/* Feature 4 */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm hover:shadow-md transition border border-gray-100 dark:border-gray-700">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/40 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Analytics Completo</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Dashboard com métricas em tempo real, gráficos de desempenho e relatórios detalhados.</p>
          </div>

          {/* Feature 5 */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm hover:shadow-md transition border border-gray-100 dark:border-gray-700">
            <div className="w-12 h-12 bg-red-100 dark:bg-red-900/40 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Segurança Avançada</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Autenticação JWT, bcrypt, criptografia de ponta a ponta e proteção contra ataques.</p>
          </div>

          {/* Feature 6 */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm hover:shadow-md transition border border-gray-100 dark:border-gray-700">
            <div className="w-12 h-12 bg-teal-100 dark:bg-teal-900/40 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-teal-600 dark:text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Multi-plataforma</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">WhatsApp e Telegram em um só lugar. Gerencie todos os canais a partir de uma interface única.</p>
          </div>
        </div>
      </section>

      {/* Plans Section */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-4">
          Planos para todos os tamanhos
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-12">
          Comece grátis e escale conforme seu negócio cresce.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Free */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">Free</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Para começar a testar</p>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              R$ 0<span className="text-sm font-normal text-gray-500">/mês</span>
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>1 Bot WhatsApp</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>100 mensagens/mês</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>50 contatos</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Automações básicas</li>
            </ul>
          </div>

          {/* Basic - Destaque */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border-2 border-purple-500 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-purple-600 text-white text-xs font-medium rounded-full">
              Popular
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">Basic</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Para pequenos negócios</p>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              R$ 49<span className="text-sm font-normal text-gray-500">/mês</span>
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>3 Bots (WhatsApp + Telegram)</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>2.000 mensagens/mês</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>500 contatos</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>IA GLM integrada</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Analytics básico</li>
            </ul>
          </div>

          {/* Pro */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">Pro</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Para equipes e empresas</p>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              R$ 149<span className="text-sm font-normal text-gray-500">/mês</span>
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>10 Bots ilimitados</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>10.000 mensagens/mês</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>5.000 contatos</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>API completa</li>
              <li className="flex items-center gap-2"><svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Suporte prioritário</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-700 py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            © 2026 AutoChat Pro. Todos os direitos reservados.
          </p>
          <div className="flex gap-4">
            <a href="http://localhost:8100/docs" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Documentação da API
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
