import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { authService } from '../../infrastructure/api/auth.service'

export default function ConfirmPhonePage() {
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [status, setStatus] = useState<'input' | 'sent' | 'verifying' | 'success' | 'error'>('input')
  const [message, setMessage] = useState('')
  const [countdown, setCountdown] = useState(0)

  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null
    if (countdown > 0) {
      interval = setInterval(() => {
        setCountdown((prev) => prev - 1)
      }, 1000)
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [countdown])

  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!phone) {
      setMessage('Por favor, insira o número de telefone.')
      return
    }

    setStatus('verifying')
    setMessage('')

    try {
      await authService.sendPhoneCode(phone)
      setStatus('sent')
      setCountdown(60) // 60 segundos cooldown
    } catch (error: any) {
      setStatus('error')
      setMessage(
        error.response?.data?.error?.message ||
          'Erro ao enviar código. Verifique o número.'
      )
    }
  }

  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault()

    if (code.length !== 6) {
      setMessage('O código deve ter 6 dígitos.')
      return
    }

    setStatus('verifying')
    setMessage('')

    try {
      await authService.verifyPhone(phone, code)
      setStatus('success')
      setMessage('Telefone confirmado com sucesso!')
    } catch (error: any) {
      setStatus('error')
      setMessage(
        error.response?.data?.error?.message ||
          'Código inválido ou expirado.'
      )
    }
  }

  const handleResend = () => {
    if (countdown === 0) {
      handleSendCode(new Event('submit') as any)
    }
  }

  const formatPhoneNumber = (value: string) => {
    // Remove tudo que não é dígito
    const cleaned = value.replace(/\D/g, '')
    // Formata para +55 (XX) XXXXX-XXXX
    if (cleaned.length <= 2) return cleaned
    if (cleaned.length <= 7) return `+55 (${cleaned.slice(0, 2)}) ${cleaned.slice(2)}`
    return `+55 (${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7, 11)}`
  }

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '')
    setPhone(value)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl mx-auto flex items-center justify-center shadow-lg mb-4">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">AutoChat Pro</h1>
          <p className="text-gray-600">Confirmar telefone</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-xl shadow-sm p-8">
          {status === 'success' ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full mx-auto mb-4 flex items-center justify-center">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">{message}</h2>
              <p className="text-gray-600 mb-6">
                Seu telefone foi confirmado e você pode usar todos os recursos do AutoChat Pro.
              </p>
              <Link
                to="/dashboard"
                className="inline-block px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium"
              >
                Ir para o Dashboard
              </Link>
            </div>
          ) : (
            <>
              {status === 'input' || status === 'error' ? (
                <>
                  <div className="mb-6">
                    <p className="text-gray-600 text-sm">
                      Digite seu número de telefone para receber um código de verificação via <strong>WhatsApp</strong> (sem custos de SMS).
                    </p>
                  </div>

                  {/* Error message */}
                  {status === 'error' && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-600">{message}</p>
                    </div>
                  )}

                  <form onSubmit={handleSendCode} className="space-y-6">
                    {/* Phone */}
                    <div>
                      <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                        Telefone (com DDD)
                      </label>
                      <div className="flex">
                        <span className="inline-flex items-center px-3 bg-gray-100 text-gray-600 text-sm border border-r-0 border-gray-300 rounded-l-lg">
                          +55
                        </span>
                        <input
                          type="tel"
                          id="phone"
                          value={formatPhoneNumber(phone)}
                          onChange={handlePhoneChange}
                          maxLength={16}
                          placeholder="(11) 99999-9999"
                          className="flex-1 px-4 py-3 border border-gray-300 rounded-r-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition"
                        />
                      </div>
                      <p className="mt-1 text-xs text-gray-500">
                        Digite apenas números: DDD + número (ex: 11999999999)
                      </p>
                    </div>

                    {/* Submit */}
                    <button
                      type="submit"
                      disabled={phone.length < 10}
                      className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Enviar código por WhatsApp
                    </button>
                  </form>
                </>
              ) : (
                <>
                  <div className="mb-6">
                    <p className="text-gray-600 text-sm">
                      Enviamos um código de 6 dígitos via WhatsApp para o número{' '}
                      <strong>{formatPhoneNumber(phone)}</strong>
                    </p>
                  </div>

                  {/* Error message - não aplica nesta branch pois status é 'sent' | 'verifying' */}
                  <form onSubmit={handleVerifyCode} className="space-y-6">
                    {/* Code */}
                    <div>
                      <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
                        Código de verificação
                      </label>
                      <input
                        type="text"
                        id="code"
                        value={code}
                        onChange={(e) => {
                          const value = e.target.value.replace(/\D/g, '').slice(0, 6)
                          setCode(value)
                        }}
                        maxLength={6}
                        className="w-full px-4 py-3 text-center text-2xl tracking-widest border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition"
                        placeholder="000000"
                      />
                    </div>

                    {/* Resend */}
                    <div className="text-center">
                      <button
                        type="button"
                        onClick={handleResend}
                        disabled={countdown > 0}
                        className="text-sm text-purple-600 hover:text-purple-700 disabled:text-gray-400 disabled:cursor-not-allowed"
                      >
                        {countdown > 0
                          ? `Reenviar em ${countdown}s`
                          : 'Reenviar código'}
                      </button>
                    </div>

                    {/* Submit */}
                    <button
                      type="submit"
                      disabled={code.length !== 6}
                      className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Verificar código
                    </button>
                  </form>
                </>
              )}

              {/* Change phone number */}
              {status === 'sent' && (
                <div className="mt-4 text-center">
                  <button
                    onClick={() => {
                      setStatus('input')
                      setCode('')
                      setMessage('')
                    }}
                    className="text-sm text-gray-600 hover:text-gray-700"
                  >
                    Número incorreto? Alterar número
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        {/* Back to dashboard */}
        <p className="mt-6 text-center text-sm text-gray-600">
          <Link to="/dashboard" className="text-purple-600 hover:text-purple-700 font-medium">
            Voltar ao Dashboard
          </Link>
        </p>
      </div>
    </div>
  )
}
