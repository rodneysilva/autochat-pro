/**
 * Serviço de integração com Telegram API.
 *
 * Comunica com os endpoints de Telegram do backend.
 */

import { getHttpClient } from './http-client'

const TELEGRAM_PATH = '/telegram'

export interface TelegramBotInfo {
  id: number
  is_bot: boolean
  first_name: string
  username: string | null
}

export const telegramService = {
  /**
   * Valida um token do Telegram (chama getMe).
   */
  async validateToken(bot_token: string): Promise<TelegramBotInfo> {
    const client = getHttpClient()
    const response = await client.post<{ ok: boolean; bot_info: TelegramBotInfo }>(
      `${TELEGRAM_PATH}/validate-token`,
      { bot_token }
    )
    return response.bot_info
  },

  /**
   * Configura webhook para um bot Telegram.
   */
  async setupWebhook(botId: string): Promise<{ ok: boolean; webhook_url: string }> {
    const client = getHttpClient()
    return client.post<{ ok: boolean; webhook_url: string }>(
      `${TELEGRAM_PATH}/setup-webhook`,
      { bot_id: botId }
    )
  },

  /**
   * Remove webhook de um bot Telegram.
   */
  async deleteWebhook(botId: string): Promise<{ ok: boolean }> {
    const client = getHttpClient()
    return client.delete<{ ok: boolean }>(`${TELEGRAM_PATH}/webhook?bot_id=${botId}`)
  },
}
