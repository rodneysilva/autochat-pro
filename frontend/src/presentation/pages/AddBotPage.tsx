import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Link } from 'react-router-dom'
import { ThemeToggle } from '../components/ui/ThemeToggle'
import { whatsappService, ConnectionStatus } from '../../infrastructure/api/whatsapp.service'

export default function AddBotPage() {
  const navigate = useNavigate()
  const [connectionMethod, setConnectionMethod] = useState<'qrcode' | 'phone'>('qrcode')
  const [instanceName, setInstanceName] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [status, setStatus] = useState<'idle' | 'connecting' | 'qrcode' | 'pairing' | 'connected' | 'error'>('idle')
  const [qrCode, setQrCode] = useState<string | null>(null)
  const [pairingCode, setPairingCode] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [timeLeft, setTimeLeft] = useState(180) // 3 minutos
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Timer de contagem regressiva
  useEffect(() => {
    if (status === 'pairing' || status === 'qrcode') {
      setTimeLeft(180)
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            if (timerRef.current) clearInterval(timerRef.current)
            setStatus('error')
            setError('Tempo esgotado. O código expirou. Tente novamente.')
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [status])

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  const formatPhoneNumber = (value: string) => {
    const cleaned = value.replace(/\D/g, '')
    if (cleaned.length <= 2) return cleaned
    if (cleaned.length <= 7) return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2)}`
    return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7, 11)}`
  }

  const handleConnect = async () => {
    if (!instanceName) {
      setError('Digite um nome para o bot')
      return
    }

    setError('')
    setStatus('connecting')

    try {
      if (connectionMethod === 'qrcode') {
        const result = await whatsappService.connectWithQRCode({
          name: instanceName,
          qrcode: true,
        })

        if (result.qrcode) {
          setQrCode(result.qrcode)
          setStatus('qrcode')
          startStatusPoll(instanceName)
        } else if (result.status === ConnectionStatus.CONNECTED) {
          setStatus('connected')
          setTimeout(() => navigate('/dashboard'), 1500)
        }
      } else {
        const cleanPhone = phoneNumber.replace(/\D/g, '')
        if (cleanPhone.length < 10) {
          setError('Número de telefone inválido')
          setStatus('idle')
          return
        }

        // Adicionar DDI 55 (Brasil) se não presente
        const fullPhone = cleanPhone.length <= 11 ? `55${cleanPhone}` : cleanPhone

        const result = await whatsappService.connectWithPhone({
          instance_name: instanceName,
          phone_number: fullPhone,
        })

        setPairingCode(result.pairing_code || JSON.stringify(result))
        setStatus('pairing')
        startStatusPoll(instanceName)
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Erro ao conectar. Tente novamente.')
      setStatus('error')
    }
  }

  const startStatusPoll = (instance: string) => {
    let pollCount = 0
    const MAX_POLLS = 90 // ~3 minutos (90 x 2s)

    const interval = setInterval(async () => {
      pollCount++
      try {
        const statusResult = await whatsappService.getStatus(instance)

        if (statusResult.connected) {
          setStatus('connected')
          clearInterval(interval)
          setQrCode(null)
          setPairingCode(null)
          setTimeout(() => navigate('/dashboard'), 1500)
          return
        }

        // Se status é "disconnected" ou "error", a conexão falhou
        if (statusResult.status === 'disconnected' || statusResult.status === 'error') {
          clearInterval(interval)
          setStatus('error')
          setError('Conexão falhou. O código pode ter expirado. Tente novamente.')
        }

        // Timeout: parar polling após MAX_POLLS
        if (pollCount >= MAX_POLLS) {
          clearInterval(interval)
          setStatus('error')
          setError('Tempo esgotado. O código de pareamento expirou. Tente novamente.')
        }
      } catch (err: any) {
        // Ignorar erros isolados, mas parar se instância não for encontrada (404)
        if (err?.response?.status === 404) {
          clearInterval(interval)
          setStatus('error')
          setError('Instância não encontrada. Tente novamente.')
        }
      }
    }, 2000)
  }

  const handleReset = () => {
    setStatus('idle')
    setQrCode(null)
    setPairingCode(null)
    setError('')
    setInstanceName('')
    setPhoneNumber('')
    setTimeLeft(180)
    if (timerRef.current) clearInterval(timerRef.current)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex flex-col">
      {/* Top bar */}
      <div className="w-full px-4 py-3 flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center gap-2 text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="text-sm font-medium">Dashboard</span>
        </Link>
        <ThemeToggle />
      </div>

      {/* Center content */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl mx-auto flex items-center justify-center shadow-lg mb-4">
              <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.548-.548-.237 0 0-.579-.657-.853-.967-.273-.31-.548-.099-.548-.099l.001.001c-.452-.198-.922-.361-1.386-.498-.198-.039-.374-.058-.548-.058-.297 0-.688.099-1.097.297l1.097-.597z"/>
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Adicionar Bot WhatsApp</h1>
            <p className="text-gray-600 dark:text-gray-400">Conecte seu WhatsApp ao AutoChat Pro</p>
          </div>

          {/* Card */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 lg:p-8">
            {status === 'connected' ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Conectado!</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-6">Seu bot WhatsApp está conectado e pronto para usar.</p>
                <p className="text-sm text-gray-500 dark:text-gray-500">Redirecionando para o dashboard...</p>
              </div>
            ) : status === 'idle' || status === 'error' ? (
              <>
                {error && (
                  <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
                    <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                  </div>
                )}

                {/* Método de conexão */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Método de conexão
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => setConnectionMethod('qrcode')}
                      className={`p-4 rounded-xl border-2 transition ${
                        connectionMethod === 'qrcode'
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-purple-300 dark:hover:border-purple-700'
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2 mb-2">
                        <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2m4 0h2m-4 0h2M4 12h16M3 12a9 9 0 1118 0 9 9 0 01-18 0z" />
                        </svg>
                        <span className="font-medium text-gray-700 dark:text-gray-300">QR Code</span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Escaneie o código</p>
                    </button>

                    <button
                      type="button"
                      onClick={() => setConnectionMethod('phone')}
                      className={`p-4 rounded-xl border-2 transition ${
                        connectionMethod === 'phone'
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-purple-300 dark:hover:border-purple-700'
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2 mb-2">
                        <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 8V5z" />
                        </svg>
                        <span className="font-medium text-gray-700 dark:text-gray-300">Telefone</span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Use seu número</p>
                    </button>
                  </div>
                </div>

                {/* Form */}
                <div className="space-y-5">
                  <div>
                    <label htmlFor="instanceName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nome do Bot
                    </label>
                    <input
                      type="text"
                      id="instanceName"
                      value={instanceName}
                      onChange={(e) => setInstanceName(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                      placeholder="Ex: Bot Atendimento 1"
                    />
                  </div>

                  {connectionMethod === 'phone' && (
                    <div>
                      <label htmlFor="phone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Seu número WhatsApp
                      </label>
                      <div className="flex">
                        <span className="inline-flex items-center px-3 bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300 text-sm border border-r-0 border-gray-300 dark:border-gray-600 rounded-l-lg">
                          +55
                        </span>
                        <input
                          type="tel"
                          id="phone"
                          value={formatPhoneNumber(phoneNumber)}
                          onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ''))}
                          maxLength={16}
                          className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-r-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                          placeholder="(11) 99999-9999"
                        />
                      </div>
                      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        Digite DDD + número (apenas números)
                      </p>
                    </div>
                  )}

                  <button
                    onClick={handleConnect}
                    disabled={!instanceName || (connectionMethod === 'phone' && phoneNumber.length < 10)}
                    className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Conectar WhatsApp
                  </button>
                </div>
              </>
            ) : status === 'qrcode' ? (
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Escaneie o QR Code</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                  Abra o WhatsApp no celular e escaneie o código abaixo
                </p>

                {qrCode && (
                  <div className="inline-block p-4 bg-white rounded-xl shadow-lg border border-gray-200 dark:border-gray-600 mb-6">
                    <img
                      src={`data:image/png;base64,${qrCode}`}
                      alt="QR Code WhatsApp"
                      className="w-64 h-64"
                    />
                  </div>
                )}

                <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  Aguardando conexão...
                  <span className={`ml-2 font-mono ${timeLeft <= 30 ? 'text-red-500 font-bold' : ''}`}>
                    {formatTime(timeLeft)}
                  </span>
                </div>

                <button onClick={handleReset} className="mt-6 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 underline">
                  Cancelar
                </button>
              </div>
            ) : status === 'pairing' ? (
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Digite o código no WhatsApp</h3>
                <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-6 mb-6">
                  <ol className="text-left text-sm text-gray-700 dark:text-gray-300 space-y-2">
                    <li className="flex gap-2">
                      <span className="font-bold text-purple-600 dark:text-purple-400">1.</span>
                      Abra o WhatsApp no seu celular
                    </li>
                    <li className="flex gap-2">
                      <span className="font-bold text-purple-600 dark:text-purple-400">2.</span>
                      Acesse: <strong>Dispositivos conectados</strong>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-bold text-purple-600 dark:text-purple-400">3.</span>
                      Toque em <strong>Vincular um telefone</strong>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-bold text-purple-600 dark:text-purple-400">4.</span>
                      Digite o código abaixo:
                    </li>
                  </ol>
                </div>

                {pairingCode && (
                  <div className="mb-6 p-4 bg-purple-50 dark:bg-purple-900/30 rounded-xl border border-purple-200 dark:border-purple-700">
                    <p className="text-3xl font-mono font-bold text-purple-700 dark:text-purple-400 tracking-wider">
                      {pairingCode}
                    </p>
                  </div>
                )}

                <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  Aguardando conexão...
                  <span className={`ml-2 font-mono ${timeLeft <= 30 ? 'text-red-500 font-bold' : ''}`}>
                    {formatTime(timeLeft)}
                  </span>
                </div>

                <button onClick={handleReset} className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 underline">
                  Cancelar
                </button>
              </div>
            ) : null}
          </div>

          {status === 'idle' && (
            <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
              <Link to="/dashboard" className="text-purple-600 dark:text-purple-400 hover:text-purple-700 font-medium">
                Voltar ao Dashboard
              </Link>
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
