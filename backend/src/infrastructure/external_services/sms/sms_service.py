"""
Serviço de envio de SMS.

Utiliza Twilio para envio de SMS transacionais
como códigos de verificação.
"""

from typing import Optional
import random

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

from src.shared.config import settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class SMSService:
    """Serviço para envio de SMS."""

    def __init__(self):
        """Configura o serviço de SMS."""
        if not TWILIO_AVAILABLE:
            logger.warning("Twilio não está instalado. SMS não estará disponível.")
            self.client = None
            return

        try:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
            )
            logger.info("Serviço SMS Twilio configurado")
        except Exception as e:
            logger.error(f"Erro ao configurar Twilio: {e}")
            self.client = None

    def generate_verification_code(self, length: int = 6) -> str:
        """
        Gera um código de verificação numérico.

        Args:
            length: Tamanho do código (padrão: 6).

        Returns:
            Código de verificação.
        """
        return "".join([str(random.randint(0, 9)) for _ in range(length)])

    async def send_verification_code(
        self,
        phone: str,
        code: str,
        app_name: str = "AutoChat Pro",
    ) -> bool:
        """
        Envia código de verificação por SMS.

        Args:
            phone: Número de telefone (formato: +5511999999999).
            code: Código de verificação.
            app_name: Nome da aplicação.

        Returns:
            True se enviado com sucesso.
        """
        if not self.client:
            logger.warning("Cliente SMS não configurado")
            return False

        try:
            message = f"Seu código de verificação {app_name} é: {code}. Válido por 10 minutos."

            twilio_message = self.client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone,
            )

            logger.info(f"SMS enviado para {phone} - SID: {twilio_message.sid}")
            return True

        except TwilioRestException as e:
            logger.error(f"Erro Twilio ao enviar SMS: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {e}")
            return False

    async def send_welcome_sms(
        self,
        phone: str,
        user_name: str,
        app_name: str = "AutoChat Pro",
    ) -> bool:
        """
        Envia SMS de boas-vindas.

        Args:
            phone: Número de telefone.
            user_name: Nome do usuário.
            app_name: Nome da aplicação.

        Returns:
            True se enviado com sucesso.
        """
        if not self.client:
            return False

        try:
            message = f"Olá {user_name}! Bem-vindo ao {app_name}. Seu cadastro foi confirmado com sucesso."

            twilio_message = self.client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone,
            )

            logger.info(f"SMS de boas-vindas enviado para {phone}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar SMS de boas-vindas: {e}")
            return False


# Instância singleton
_sms_service: Optional[SMSService] = None


def get_sms_service() -> SMSService:
    """Retorna instância do serviço de SMS."""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service
