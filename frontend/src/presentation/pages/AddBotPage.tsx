import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Link } from 'react-router-dom'
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
  const [checkingStatus, setCheckingStatus] = useState(false)

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

          // Poll para verificar status
          startStatusPoll(instanceName)
        } else if (result.status === ConnectionStatus.CONNECTED) {
          setStatus('connected')
          setTimeout(() => navigate('/dashboard'), 1500)
        }
      } else {
        // Conexão por telefone
        const cleanPhone = phoneNumber.replace(/\D/g, '')
        if (cleanPhone.length < 10) {
          setError('Número de telefone inválido')
          setStatus('idle')
          return
        }

        const result = await whatsappService.connectWithPhone({
          instance_name: instanceName,
          phone_number: cleanPhone,
        })

        setPairingCode(result.pairing_code || result.code || JSON.stringify(result))
        setStatus('pairing')

        // Poll para verificar status
        startStatusPoll(instanceName)
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Erro ao conectar. Tente novamente.')
      setStatus('error')
    }
  }

  const startStatusPoll = (instance: string) => {
    const interval = setInterval(async () => {
      try {
        const statusResult = await whatsappService.getStatus(instance)

        if (statusResult.connected) {
          setStatus('connected')
          clearInterval(interval)
          setQrCode(null)
          setPairingCode(null)
          setTimeout(() => navigate('/dashboard'), 1500)
        }
      } catch (err) {
        // Ignorar erros durante polling
      }
    }, 2000)

    // Parar após 5 minutos
    setTimeout(() => clearInterval(interval), 300000)
  }

  const handleReset = () => {
    setStatus('idle')
    setQrCode(null)
    setPairingCode(null)
    setError('')
    setInstanceName('')
    setPhoneNumber('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl mx-auto flex items-center justify-center shadow-lg mb-4">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.548-.548-.237 0 0-.579-.657-.853-.967-.273-.31-.548-.099-.548-.099.452-.198.922-.361 1.386-.498.198-.039.374-.058.548-.058.297 0 .688.099 1.097.297.498.298.907.696 1.236 1.097.249.298.548.597.896.696.298.099.548.199.847.199.846 0 .498-.058.946-.199 1.385-.597.946-.498 1.674-1.028 2.266-1.526.498-.498.896-1.196 1.326-1.993.696-.996 1.326-2.07 1.526-3.23.199-1.195-.199-2.664-.598-4.229-1.595-2.364-1.395-4.229-3.529-5.324-6.386-.996-2.763-.696-5.524.498-7.884 1.096-2.363 3.628-3.829 6.384-4.328 2.762-.498 5.523.199 7.885.696 1.196.498 2.364 1.595 3.23 2.991.996 1.396 1.495 3.062 1.595 5.229 0 2.164-.598 3.829-1.595 4.924-.997 1.096-2.564 1.595-4.924 1.595-.498 0-.996-.05-1.495-.149-.498-.099-.996-.248-1.495-.397l-.996 1.495c-.498.796-.996 1.594-1.495 2.39-.498.796-.996 1.593-1.495 2.39-.498.796-.996 1.593-1.495 2.39-.498.796-.996 1.593-1.495 2.39l-1.495 2.39c-.498.796-.996 1.593-1.495 2.39-.498.796-.996 1.593-1.495 2.39-.498.796-.996 1.593-1.495 2.39z"/>
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Adicionar Bot WhatsApp</h1>
          <p className="text-gray-600">Conecte seu WhatsApp ao AutoChat Pro</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-xl shadow-sm p-8">
          {status === 'connected' ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-100 rounded-full mx-auto mb-4 flex items-center justify-center">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Conectado!</h2>
              <p className="text-gray-600 mb-6">Seu bot WhatsApp está conectado e pronto para usar.</p>
              <p className="text-sm text-gray-500">Redirecionando para o dashboard...</p>
            </div>
          ) : status === 'idle' || status === 'error' ? (
            <>
              {/* Error */}
              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {/* Método de conexão */}
              <div className="mb-8">
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Método de conexão
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setConnectionMethod('qrcode')}
                    className={`p-4 rounded-xl border-2 transition ${
                      connectionMethod === 'qrcode'
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2m4 0h2m-4 0h2M4 12h16M3 12a9 9 0 1118 0 9 9 0 01-18 0z" />
                      </svg>
                      <span className="font-medium text-gray-700">QR Code</span>
                    </div>
                    <p className="text-xs text-gray-500">Escaneie o código no WhatsApp</p>
                  </button>

                  <button
                    type="button"
                    onClick={() => setConnectionMethod('phone')}
                    className={`p-4 rounded-xl border-2 transition ${
                      connectionMethod === 'phone'
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 8V5z" />
                      </svg>
                      <span className="font-medium text-gray-700">Telefone</span>
                    </div>
                    <p className="text-xs text-gray-500">Use seu número</p>
                  </button>
                </div>
              </div>

              {/* Form */}
              <div className="space-y-6">
                {/* Nome do Bot */}
                <div>
                  <label htmlFor="instanceName" className="block text-sm font-medium text-gray-700 mb-2">
                    Nome do Bot
                  </label>
                  <input
                    type="text"
                    id="instanceName"
                    value={instanceName}
                    onChange={(e) => setInstanceName(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition"
                    placeholder="Ex: Bot Atendimento 1"
                  />
                </div>

                {/* Número (apenas phone method) */}
                {connectionMethod === 'phone' && (
                  <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                      Seu número WhatsApp
                    </label>
                    <div className="flex">
                      <span className="inline-flex items-center px-3 bg-gray-100 text-gray-600 text-sm border border-r-0 border-gray-300 rounded-l-lg">
                        +55
                      </span>
                      <input
                        type="tel"
                        id="phone"
                        value={formatPhoneNumber(phoneNumber)}
                        onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ''))}
                        maxLength={16}
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-r-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition"
                        placeholder="(11) 99999-9999"
                      />
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      Digite DDD + número (apenas números)
                    </p>
                  </div>
                )}

                {/* Submit */}
                <button
                  onClick={handleConnect}
                  disabled={status === 'connecting' || !instanceName || (connectionMethod === 'phone' && phoneNumber.length < 10)}
                  className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {status === 'connecting' ? 'Conectando...' : 'Conectar WhatsApp'}
                </button>
              </div>
            </>
          ) : status === 'qrcode' ? (
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Escaneie o QR Code</h3>
              <p className="text-sm text-gray-600 mb-6">
                Abra o WhatsApp no seu celular e escaneie o código abaixo
              </p>

              {qrCode && (
                <div className="inline-block p-4 bg-white rounded-xl shadow-lg border border-gray-200 mb-6">
                  <img
                    src={`data:image/png;base64,${qrCode}`}
                    alt="QR Code WhatsApp"
                    className="w-64 h-64"
                  />
                </div>
              )}

              <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Aguardando conexão...
              </div>

              <button
                onClick={handleReset}
                className="mt-6 text-sm text-gray-600 hover:text-gray-700 underline"
              >
                Cancelar
              </button>
            </div>
          ) : status === 'pairing' ? (
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Digite o código no WhatsApp</h3>
              <div className="bg-gray-100 rounded-xl p-6 mb-6">
                <ol className="text-left text-sm text-gray-700 space-y-2">
                  <li className="flex gap-2">
                    <span className="font-bold text-purple-600">1.</span>
                    Abra o WhatsApp no seu celular
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold text-purple-600">2.</span>
                    Acesse: <strong>Dispositivos conectados</strong>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold text-purple-600">3.</span>
                    Toque em <strong>Vincular um telefone</strong>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold text-purple-600">4.</span>
                    Digite o código abaixo:
                  </li>
                </ol>
              </div>

              {pairingCode && (
                <div className="mb-6 p-4 bg-purple-50 rounded-xl border border-purple-200">
                  <p className="text-3xl font-mono font-bold text-purple-700 tracking-wider">
                    {pairingCode}
                  </p>
                </div>
              )}

              <div className="flex items-center justify-center gap-2 text-sm text-gray-500 mb-4">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Aguardando conexão...
              </div>

              <button
                onClick={handleReset}
                className="text-sm text-gray-600 hover:text-gray-700 underline"
              >
                Cancelar
              </button>
            </div>
          ) : null}
        </div>

        {/* Back */}
        {status === 'idle' && (
          <p className="mt-6 text-center text-sm text-gray-600">
            <Link to="/dashboard" className="text-purple-600 hover:text-purple-700 font-medium">
              Voltar ao Dashboard
            </Link>
          </p>
        )}
      </div>
    </div>
  )
}
