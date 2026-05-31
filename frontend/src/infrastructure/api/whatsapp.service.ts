/**
 * Serviço de integração WhatsApp.
 *
 * Comunica com a API de WhatsApp para gerenciar instâncias,
 * QR Code, conexão por telefone e envio de mensagens.
 */

import { getHttpClient } from './http-client'

export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  QR_CODE = 'qr_code',
  TIMEOUT = 'timeout',
  ERROR = 'error',
}

interface CreateInstanceRequest {
  name: string
  qrcode?: boolean
}

interface ConnectWithPhoneRequest {
  instance_name: string
  phone_number: string
}

interface SendTextRequest {
  instance_name: string
  phone_number: string
  message: string
  delay?: number
}

interface SendMediaRequest {
  instance_name: string
  phone_number: string
  media_url: string
  caption?: string
  media_type?: string
}

interface SetWebhookRequest {
  webhook_url: string
  events?: string[]
  webhook_by_events?: boolean
}

interface Instance {
  name: string
  status: ConnectionStatus
  qrcode?: string
  phone_connected?: string
  created_at?: string
}

interface SendMessageResponse {
  message: string
  message_id: string
}

const WHATSAPP_PATH = '/whatsapp'

export const whatsappService = {
  /**
   * Cria uma nova instância WhatsApp.
   */
  async createInstance(data: CreateInstanceRequest): Promise<Instance> {
    const client = getHttpClient()
    return client.post<Instance>(`${WHATSAPP_PATH}/instances`, data)
  },

  /**
   * Lista todas as instâncias.
   */
  async listInstances(): Promise<{ instances: Instance[] }> {
    const client = getHttpClient()
    return client.get(`${WHATSAPP_PATH}/instances`)
  },

  /**
   * Obtém informações de uma instância.
   */
  async getInstance(instanceName: string): Promise<Instance> {
    const client = getHttpClient()
    return client.get<Instance>(`${WHATSAPP_PATH}/instances/${instanceName}`)
  },

  /**
   * Deleta uma instância.
   */
  async deleteInstance(instanceName: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.delete<{ message: string }>(`${WHATSAPP_PATH}/instances/${instanceName}`)
  },

  /**
   * Faz logout de uma instância.
   */
  async logout(instanceName: string): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.post<{ message: string }>(`${WHATSAPP_PATH}/instances/${instanceName}/logout`)
  },

  /**
   * Conecta via QR Code.
   */
  async connectWithQRCode(data: CreateInstanceRequest): Promise<Instance> {
    const client = getHttpClient()
    return client.post<Instance>(`${WHATSAPP_PATH}/connect/qrcode`, data)
  },

  /**
   * Obtém QR Code de uma instância.
   */
  async getQRCode(instanceName: string): Promise<{ instance: string; qrcode: string }> {
    const client = getHttpClient()
    return client.get(`${WHATSAPP_PATH}/instances/${instanceName}/qrcode`)
  },

  /**
   * Conecta via número de telefone.
   */
  async connectWithPhone(data: ConnectWithPhoneRequest): Promise<{
    instance: string
    message: string
    pairing_code: string
    status: ConnectionStatus
  }> {
    const client = getHttpClient()
    return client.post(`${WHATSAPP_PATH}/connect/phone`, data)
  },

  /**
   * Verifica status da conexão por telefone.
   */
  async checkPhoneStatus(instanceName: string): Promise<{
    instance: string
    status: ConnectionStatus
    details: any
  }> {
    const client = getHttpClient()
    return client.get(`${WHATSAPP_PATH}/instances/${instanceName}/phone/status`)
  },

  /**
   * Envia mensagem de texto.
   */
  async sendText(data: SendTextRequest): Promise<SendMessageResponse> {
    const client = getHttpClient()
    return client.post<SendMessageResponse>(`${WHATSAPP_PATH}/send/text`, data)
  },

  /**
   * Envia mensagem com mídia.
   */
  async sendMedia(data: SendMediaRequest): Promise<SendMessageResponse> {
    const client = getHttpClient()
    return client.post<SendMessageResponse>(`${WHATSAPP_PATH}/send/media`, data)
  },

  /**
   * Obtém mensagens de uma instância.
   */
  async getMessages(instanceName: string, limit = 100): Promise<{
    instance: string
    messages: any[]
  }> {
    const client = getHttpClient()
    return client.get(`${WHATSAPP_PATH}/instances/${instanceName}/messages?limit=${limit}`)
  },

  /**
   * Obtém status de uma instância.
   */
  async getStatus(instanceName: string): Promise<{
    instance: string
    status: ConnectionStatus
    connected: boolean
  }> {
    const client = getHttpClient()
    return client.get(`${WHATSAPP_PATH}/instances/${instanceName}/status`)
  },

  /**
   * Configura webhook.
   */
  async setWebhook(instanceName: string, data: SetWebhookRequest): Promise<{ message: string }> {
    const client = getHttpClient()
    return client.post(`${WHATSAPP_PATH}/instances/${instanceName}/webhook`, data)
  },

  /**
   * Obtém configuração de webhook.
   */
  async getWebhook(instanceName: string): Promise<{ instance: string; webhook: any }> {
    const client = getHttpClient()
    return client.get(`${WHATSAPP_PATH}/instances/${instanceName}/webhook`)
  },
}
