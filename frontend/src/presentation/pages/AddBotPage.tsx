import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Link } from 'react-router-dom'
import { ThemeToggle } from '../components/ui/ThemeToggle'
import { whatsappService, ConnectionStatus } from '../../infrastructure/api/whatsapp.service'

type ConnectionMethod = 'qrcode' | 'phone'

export default function AddBotPage() {
  const navigate = useNavigate()
  const [instanceName, setInstanceName] = useState('')
  const [waMethod, setWaMethod] = useState<ConnectionMethod>('phone')
  const [waPhone, setWaPhone] = useState('')
  const [status, setStatus] = useState<'idle' | 'connecting' | 'qrcode' | 'pairing' | 'connected' | 'error'>('idle')
  const [qrCode, setQrCode] = useState<string | null>(null)
  const [pairingCode, setPairingCode] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [timeLeft, setTimeLeft] = useState(180)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (status === 'qrcode' || status === 'pairing') {
      setTimeLeft(180)
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            if (timerRef.current) clearInterval(timerRef.current)
            setStatus('error')
            setError('Tempo esgotado. Tente novamente.')
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

    if (waMethod === 'phone' && waPhone.replace(/\D/g, '').length < 10) {
      setError('Digite um número de telefone válido')
      return
    }

    setError('')
    setStatus('connecting')

    try {
      if (waMethod === 'phone') {
        const cleanPhone = waPhone.replace(/\D/g, '')
        const fullPhone = cleanPhone.length <= 11 ? `55${cleanPhone}` : cleanPhone

        const result = await whatsappService.connectWithPhone({
          instance_name: instanceName,
          phone_number: fullPhone,
        })

        if (result.pairing_code) {
          setPairingCode(result.pairing_code)
          setStatus('pairing')
          startStatusPoll(instanceName)
        } else {
          setError('Não foi possível gerar o código. Tente novamente.')
          setStatus('error')
        }
      } else {
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
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || err.response?.data?.detail?.erro?.mensagem || 'Erro ao conectar. Tente novamente.')
      setStatus('error')
    }
  }

  const startStatusPoll = (instance: string) => {
    let pollCount = 0
    const MAX_POLLS = 90
    let botSaved = false

    const interval = setInterval(async () => {
      pollCount++
      try {
        // Só confiar no status real da Evolution
        const statusResult = await whatsappService.getStatus(instance)

        if (statusResult.connected) {
          setStatus('connected')
          clearInterval(interval)
          setQrCode(null)
          setPairingCode(null)

          // Salvar bot no banco (só uma vez)
          if (!botSaved) {
            botSaved = true
            try {
              const { botsService } = await import('../../infrastructure/api/bots.service')
              const botsResponse = await botsService.list()
              const existingBot = botsResponse.data.find((b: any) => b.nome === instance)
              if (existingBot) {
                await botsService.resume(existingBot.id)
              } else {
                await botsService.create({ nome: instance, tipo: 'whatsapp' })
              }
            } catch (err) {
              console.error('Erro ao salvar bot:', err)
            }
          }

          setTimeout(() => navigate('/dashboard'), 2000)
          return
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
    }, 3000)
  }

  const handleReset = () => {
    setStatus('idle')
    setQrCode(null)
    setPairingCode(null)
    setError('')
    setInstanceName('')
    setWaPhone('')
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
              <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
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

                  {/* Método de conexão */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Método de conexão
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        type="button"
                        onClick={() => setWaMethod('phone')}
                        className={`p-4 rounded-xl border-2 transition ${
                          waMethod === 'phone'
                            ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                            : 'border-gray-200 dark:border-gray-600 hover:border-purple-300'
                        }`}
                      >
                        <div className="flex items-center justify-center gap-2 mb-1">
                          <span className="text-lg">📱</span>
                          <span className="font-medium text-gray-700 dark:text-gray-300 text-sm">Telefone</span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Digite seu número</p>
                      </button>

                      <button
                        type="button"
                        onClick={() => setWaMethod('qrcode')}
                        className={`p-4 rounded-xl border-2 transition ${
                          waMethod === 'qrcode'
                            ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                            : 'border-gray-200 dark:border-gray-600 hover:border-purple-300'
                        }`}
                      >
                        <div className="flex items-center justify-center gap-2 mb-1">
                          <span className="text-lg">📷</span>
                          <span className="font-medium text-gray-700 dark:text-gray-300 text-sm">QR Code</span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Escaneie o código</p>
                      </button>
                    </div>
                  </div>

                  {/* Campo de telefone */}
                  {waMethod === 'phone' && (
                    <div>
                      <label htmlFor="waPhone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Seu número WhatsApp
                      </label>
                      <div className="flex">
                        <span className="inline-flex items-center px-3 bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300 text-sm border border-r-0 border-gray-300 dark:border-gray-600 rounded-l-lg">
                          +55
                        </span>
                        <input
                          type="tel"
                          id="waPhone"
                          value={waPhone}
                          onChange={(e) => setWaPhone(e.target.value.replace(/\D/g, ''))}
                          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-r-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                          placeholder="(11) 99999-9999"
                          maxLength={15}
                        />
                      </div>
                    </div>
                  )}

                  <button
                    onClick={handleConnect}
                    disabled={!instanceName || (waMethod === 'phone' && waPhone.replace(/\D/g, '').length < 10)}
                    className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {waMethod === 'phone' ? 'Conectar via Telefone' : 'Conectar via QR Code'}
                  </button>
                </div>
              </>
            ) : status === 'pairing' ? (
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Código de Pareamento</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                  No WhatsApp: Dispositivos conectados → Vincular → Digitar número
                </p>

                {pairingCode && (
                  <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-6 mb-4">
                    <p className="text-3xl font-mono font-bold text-purple-600 dark:text-purple-400 tracking-widest">
                      {pairingCode}
                    </p>
                  </div>
                )}

                <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  Aguardando conexão...
                  <span className={`ml-2 font-mono ${timeLeft <= 30 ? 'text-red-500 font-bold' : ''}`}>
                    {formatTime(timeLeft)}
                  </span>
                </div>

                <button onClick={handleReset} className="mt-4 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-700 underline">
                  Cancelar
                </button>
              </div>
            ) : status === 'qrcode' ? (
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Escaneie o QR Code</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Abra o WhatsApp → Dispositivos conectados → Vincular
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
                <p className="text-gray-600 dark:text-gray-400">
                  {waMethod === 'phone' ? 'Gerando código de pareamento...' : 'Gerando QR Code...'}
                </p>
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
