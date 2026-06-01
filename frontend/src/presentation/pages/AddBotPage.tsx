import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Link } from 'react-router-dom'
import { ThemeToggle } from '../components/ui/ThemeToggle'
import { whatsappService, ConnectionStatus } from '../../infrastructure/api/whatsapp.service'

export default function AddBotPage() {
  const navigate = useNavigate()
  const [instanceName, setInstanceName] = useState('')
  const [status, setStatus] = useState<'idle' | 'connecting' | 'qrcode' | 'connected' | 'error'>('idle')
  const [qrCode, setQrCode] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [timeLeft, setTimeLeft] = useState(180)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (status === 'qrcode') {
      setTimeLeft(180)
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            if (timerRef.current) clearInterval(timerRef.current)
            setStatus('error')
            setError('Tempo esgotado. O QR Code expirou. Tente novamente.')
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

  const handleConnect = async () => {
    if (!instanceName) {
      setError('Digite um nome para o bot')
      return
    }

    setError('')
    setStatus('connecting')

    try {
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
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Erro ao conectar. Tente novamente.')
      setStatus('error')
    }
  }

  const startStatusPoll = (instance: string) => {
    let pollCount = 0
    const MAX_POLLS = 90

    const interval = setInterval(async () => {
      pollCount++
      try {
        const statusResult = await whatsappService.getStatus(instance)
        let isConnected = statusResult.connected

        if (!isConnected) {
          try {
            const phoneResult = await whatsappService.checkPhoneStatus(instance)
            if ((phoneResult.status as string) !== 'pairing' && (phoneResult.status as string) !== 'disconnected') {
              isConnected = true
            }
          } catch {}
        }

        if (isConnected) {
          setStatus('connected')
          clearInterval(interval)
          setQrCode(null)

          try {
            const { botsService } = await import('../../infrastructure/api/bots.service')
            let botCreated = false
            try {
              const botsResponse = await botsService.list()
              const existingBot = botsResponse.data.find((b: any) => b.nome === instance)
              if (existingBot) {
                await botsService.resume(existingBot.id)
                botCreated = true
              }
            } catch {}

            if (!botCreated) {
              try {
                await botsService.create({ nome: instance, tipo: 'whatsapp' })
              } catch (createErr: any) {
                try {
                  const botsResponse = await botsService.list()
                  const existingBot = botsResponse.data.find((b: any) => b.nome === instance)
                  if (existingBot) await botsService.resume(existingBot.id)
                } catch {}
              }
            }
          } catch (err) {
            console.error('Erro ao salvar bot:', err)
          }

          setTimeout(() => navigate('/dashboard'), 1500)
          return
        }

        if (statusResult.status === 'disconnected' || statusResult.status === 'error') {
          clearInterval(interval)
          setStatus('error')
          setError('Conexão falhou. Tente novamente.')
        }

        if (pollCount >= MAX_POLLS) {
          clearInterval(interval)
          setStatus('error')
          setError('Tempo esgotado. Tente novamente.')
        }
      } catch (err: any) {
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
    setError('')
    setInstanceName('')
    setTimeLeft(180)
    if (timerRef.current) clearInterval(timerRef.current)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex flex-col">
      <div className="w-full px-4 py-3 flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center gap-2 text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="text-sm font-medium">Dashboard</span>
        </Link>
        <ThemeToggle />
      </div>

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl mx-auto flex items-center justify-center shadow-lg mb-4">
              <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.548-.548-.237 0 0-.579-.657-.853-.967-.273-.31-.548-.099-.548-.099l.001.001c-.452-.198-.922-.361-1.386-.498-.198-.039-.374-.058-.548-.058-.297 0-.688.099-1.097.297l1.097-.597z"/>
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Adicionar Bot WhatsApp</h1>
            <p className="text-gray-600 dark:text-gray-400">Conecte seu WhatsApp ao AutoChat Pro</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
            {status === 'connected' ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Conectado!</h2>
                <p className="text-gray-600 dark:text-gray-400">Redirecionando...</p>
              </div>
            ) : status === 'idle' || status === 'error' ? (
              <>
                {error && (
                  <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
                    <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                  </div>
                )}

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
                      placeholder="Ex: Atendimento"
                    />
                  </div>

                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      📷 Clique em conectar para gerar o QR Code e escaneie no WhatsApp do celular
                    </p>
                  </div>

                  <button
                    onClick={handleConnect}
                    disabled={!instanceName}
                    className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Conectar via QR Code
                  </button>
                </div>
              </>
            ) : status === 'qrcode' ? (
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Escaneie o QR Code</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Abra o WhatsApp no celular → Dispositivos conectados → Vincular
                </p>

                {qrCode && (
                  <div className="inline-block p-3 bg-white rounded-xl shadow-lg border border-gray-200 dark:border-gray-600 mb-4">
                    <img
                      src={`data:image/png;base64,${qrCode}`}
                      alt="QR Code WhatsApp"
                      className="w-64 h-64"
                    />
                  </div>
                )}

                <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  Aguardando escaneamento...
                  <span className={`ml-2 font-mono ${timeLeft <= 30 ? 'text-red-500 font-bold' : ''}`}>
                    {formatTime(timeLeft)}
                  </span>
                </div>

                <button onClick={handleReset} className="mt-4 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-700 underline">
                  Cancelar
                </button>
              </div>
            ) : status === 'connecting' ? (
              <div className="text-center py-8">
                <div className="w-8 h-8 border-2 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Gerando QR Code...</p>
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
