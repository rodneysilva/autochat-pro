"""
Serviço de envio de emails.

Utiliza FastAPI-Mail para envio de emails transacionais
com templates HTML.
"""

from typing import List, Optional
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi_mail.email_utils import DefaultSchemas

from src.shared.config import settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

# Diretório de templates de email
TEMPLATES_DIR = Path(__file__).parent / "templates"


class EmailSchema:
    """Esquema para configuração de email."""

    def __init__(
        self,
        email: List[str],
        subject: str,
        body: Optional[str] = None,
        template_name: Optional[str] = None,
        template_data: Optional[dict] = None,
        subtype: MessageType = MessageType.html,
    ):
        self.email = email
        self.subject = subject
        self.body = body
        self.template_name = template_name
        self.template_data = template_data or {}
        self.subtype = subtype


class EmailService:
    """Serviço para envio de emails."""

    def __init__(self):
        """Configura o serviço de email."""
        self.email_config = {
            "MAIL_USERNAME": settings.MAIL_USERNAME,
            "MAIL_PASSWORD": settings.MAIL_PASSWORD,
            "MAIL_FROM": settings.MAIL_FROM,
            "MAIL_PORT": settings.MAIL_PORT,
            "MAIL_SERVER": settings.MAIL_SERVER,
            "MAIL_FROM_NAME": settings.MAIL_FROM_NAME,
            "MAIL_STARTTLS": settings.MAIL_STARTTLS,
            "MAIL_SSL_TLS": settings.MAIL_SSL_TLS,
            "USE_CREDENTIALS": True,
            "VALIDATE_CERTS": True,
        }

        self.fastmail = FastMail(self.email_config)

    async def send_email(self, email_schema: EmailSchema) -> bool:
        """
        Envia um email.

        Args:
            email_schema: Esquema do email a ser enviado.

        Returns:
            True se enviado com sucesso.
        """
        try:
            if email_schema.template_name:
                # Usar template
                template_path = TEMPLATES_DIR / email_schema.template_name

                message = MessageSchema(
                    subject=email_schema.subject,
                    recipients=email_schema.email,
                    template_body=email_schema.template_data,
                    subtype=email_schema.subtype,
                    html_template=str(template_path),
                )
            else:
                # Usar corpo direto
                message = MessageSchema(
                    subject=email_schema.subject,
                    recipients=email_schema.email,
                    body=email_schema.body,
                    subtype=email_schema.subtype,
                )

            await self.fastmail.send_message(message)
            logger.info(f"Email enviado para {email_schema.email}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            raise

    async def send_confirmation_email(
        self,
        to_email: str,
        user_name: str,
        confirmation_link: str,
    ) -> bool:
        """
        Envia email de confirmação de cadastro.

        Args:
            to_email: Email do destinatário.
            user_name: Nome do usuário.
            confirmation_link: Link de confirmação.

        Returns:
            True se enviado com sucesso.
        """
        return await self.send_email(
            EmailSchema(
                email=[to_email],
                subject="Confirme seu email - AutoChat Pro",
                template_name="confirmation_email.html",
                template_data={
                    "user_name": user_name,
                    "confirmation_link": confirmation_link,
                    "app_name": "AutoChat Pro",
                },
            )
        )

    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_link: str,
    ) -> bool:
        """
        Envia email de recuperação de senha.

        Args:
            to_email: Email do destinatário.
            user_name: Nome do usuário.
            reset_link: Link de reset de senha.

        Returns:
            True se enviado com sucesso.
        """
        return await self.send_email(
            EmailSchema(
                email=[to_email],
                subject="Recupere sua senha - AutoChat Pro",
                template_name="password_reset.html",
                template_data={
                    "user_name": user_name,
                    "reset_link": reset_link,
                    "app_name": "AutoChat Pro",
                },
            )
        )

    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
    ) -> bool:
        """
        Envia email de boas-vindas após confirmação.

        Args:
            to_email: Email do destinatário.
            user_name: Nome do usuário.

        Returns:
            True se enviado com sucesso.
        """
        return await self.send_email(
            EmailSchema(
                email=[to_email],
                subject="Bem-vindo ao AutoChat Pro!",
                template_name="welcome_email.html",
                template_data={
                    "user_name": user_name,
                    "app_name": "AutoChat Pro",
                    "dashboard_link": f"{settings.FRONTEND_URL}/dashboard",
                },
            )
        )


# Instância singleton
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Retorna instância do serviço de email."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
