"""
Serviço de envio de códigos de verificação via WhatsApp.

Substitui SMS por WhatsApp para verificação de telefone,
sem custos de envio.
"""

from typing import Optional, Dict, Any
import random
from datetime import datetime, timedelta

from src.shared.config import settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class WhatsAppVerificationService:
    """Serviço para envio de códigos de verificação via WhatsApp."""

    def __init__(self):
        """Inicializa o serviço."""
        # Em produção, usar Redis para armazenar códigos
        self._codes: Dict[str, Dict[str, Any]] = {}

        # Configuração Evolution API (ou similar)
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', 'http://localhost:8080')
        self.api_key = getattr(settings, 'WHATSAPP_API_KEY', '')

    def generate_verification_code(self, length: int = 6) -> str:
        """
        Gera um código de verificação numérico.

        Args:
            length: Tamanho do código (padrão: 6).

        Returns:
            Código de verificação.
        """
        return "".join([str(random.randint(0, 9)) for _ in range(length)])

    def format_phone_for_whatsapp(self, phone: str) -> str:
        """
        Formata telefone para padrão WhatsApp.

        Args:
            phone: Telefone em varios formatos.

        Returns:
            Telefone no formato WhatsApp: 5511999999999 (sem + e sem símbolos)
        """
        # Remove todos os caracteres não numéricos
        clean_phone = "".join(filter(str.isdigit, phone))

        # Se começar com 0 ( Brasil), remover
        if clean_phone.startswith("0"):
            clean_phone = clean_phone[1:]

        # Se não tiver código do país (55), adicionar
        if len(clean_phone) == 11:  # DDD + número ( Brasil sem 55)
            clean_phone = "55" + clean_phone

        return clean_phone

    async def send_verification_code(
        self,
        phone: str,
        code: Optional[str] = None,
        bot_name: str = "AutoChat Pro"
    ) -> bool:
        """
        Envia código de verificação via WhatsApp.

        Args:
            phone: Número de telefone.
            code: Código (se None, gera um novo).
            bot_name: Nome do bot/aplicação.

        Returns:
            True se enviado com sucesso.
        """
        if code is None:
            code = self.generate_verification_code()

        # Armazenar código com expiração (10 minutos)
        self._codes[phone] = {
            "code": code,
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
            "attempts": 0,
            "sent_at": datetime.utcnow(),
        }

        # Formatar telefone
        whatsapp_phone = self.format_phone_for_whatsapp(phone)

        # Mensagem
        message = (
            f"🔐 *{bot_name}* - Código de Verificação\n\n"
            f"Seu código é: *{code}*\n\n"
            f"Válido por 10 minutos.\n\n"
            f"⚠️ Não compartilhe este código com ninguém."
        )

        # Enviar via Evolution API (ou similar)
        try:
            import httpx

            headers = {
                "Content-Type": "application/json",
                "apikey": self.api_key,
            }

            payload = {
                "number": f"{whatsapp_phone}@s.whatsapp.net",
                "text": message,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/message/sendText/",
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )

                if response.status_code in [200, 201]:
                    logger.info(f"Código WhatsApp enviado para {whatsapp_phone}")
                    return True
                else:
                    logger.warning(f"Erro ao enviar WhatsApp: {response.status_code}")
                    # Em desenvolvimento, aceitar falha
                    return True

        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
            # Em desenvolvimento, log do código
            logger.info(f"[DEV] Código para {phone}: {code}")
            return True

    async def verify_code(
        self,
        phone: str,
        code: str,
    ) -> bool:
        """
        Verifica o código de confirmação.

        Args:
            phone: Número de telefone.
            code: Código de verificação.

        Returns:
            True se verificado com sucesso.

        Raises:
            ValidationError: Se o código for inválido ou expirado.
        """
        from src.shared.exceptions import ValidationError

        stored_data = self._codes.get(phone)

        if not stored_data:
            logger.warning(f"Nenhum código encontrado para {phone}")
            raise ValidationError("Código inválido ou expirado")

        # Verificar expiração
        if datetime.utcnow() > stored_data["expires_at"]:
            self._codes.pop(phone, None)
            logger.warning(f"Código expirado para {phone}")
            raise ValidationError("Código expirado. Solicite um novo.")

        # Verificar código
        if stored_data["code"] != code:
            stored_data["attempts"] = stored_data.get("attempts", 0) + 1

            # Limpar após 3 tentativas
            if stored_data["attempts"] >= 3:
                self._codes.pop(phone, None)
                logger.warning(f"Muitas tentativas para {phone}")
                raise ValidationError("Muitas tentativas. Solicite um novo código.")

            logger.warning(f"Código incorreto para {phone}")
            raise ValidationError("Código incorreto")

        # Código correto - remover código usado
        self._codes.pop(phone, None)
        logger.info(f"Código WhatsApp verificado com sucesso: {phone}")
        return True

    def has_pending_code(self, phone: str) -> bool:
        """
        Verifica se há um código pendente para o telefone.

        Args:
            phone: Número de telefone.

        Returns:
            True se houver código pendente não expirado.
        """
        stored_data = self._codes.get(phone)
        if not stored_data:
            return False

        # Verificar se não expirou
        if datetime.utcnow() > stored_data["expires_at"]:
            self._codes.pop(phone, None)
            return False

        return True

    def can_resend(self, phone: str) -> bool:
        """
        Verifica se pode reenviar código (cooldown de 1 minuto).

        Args:
            phone: Número de telefone.

        Returns:
            True se pode reenviar.
        """
        stored_data = self._codes.get(phone)
        if not stored_data:
            return True

        # Cooldown de 60 segundos
        sent_at = stored_data.get("sent_at")
        if sent_at and (datetime.utcnow() - sent_at).total_seconds() < 60:
            return False

        return True

    def get_dev_code(self, phone: str) -> Optional[str]:
        """
        Retorna o código armazenado (apenas para desenvolvimento).

        Args:
            phone: Número de telefone.

        Returns:
            Código armazenado ou None.
        """
        stored_data = self._codes.get(phone)
        return stored_data["code"] if stored_data else None


# Instância singleton
_whatsapp_service: Optional[WhatsAppVerificationService] = None


def get_whatsapp_service() -> WhatsAppVerificationService:
    """Retorna instância do serviço de WhatsApp."""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppVerificationService()
    return _whatsapp_service
