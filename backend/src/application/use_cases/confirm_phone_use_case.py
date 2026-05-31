"""
Caso de uso de confirmação de telefone.

Implementa a geração e validação de código de verificação
enviado por SMS.
"""

from typing import Optional
from datetime import datetime, timedelta

from src.domain.repositories.user_repository import UserRepository
from src.shared.exceptions import InvalidTokenException, UnauthorizedError, ValidationError
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class ConfirmPhoneUseCase:
    """Caso de uso para confirmação de telefone."""

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa o caso de uso.

        Args:
            user_repository: Repositório de usuários.
        """
        self._repository = user_repository
        # Em produção, usar Redis para armazenar códigos
        self._codes = {}  # {phone: {"code": "123456", "expires_at": datetime}}

    async def send_verification_code(
        self,
        phone: str,
    ) -> bool:
        """
        Envia código de verificação por WhatsApp.

        Args:
            phone: Número de telefone.

        Returns:
            True se enviado com sucesso.
        """
        from src.infrastructure.external_services.whatsapp import get_whatsapp_service

        whatsapp_service = get_whatsapp_service()

        # Gerar código localmente
        code = whatsapp_service.generate_verification_code()

        # Armazenar código com expiração (10 minutos)
        self._codes[phone] = {
            "code": code,
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
            "attempts": 0,
            "sent_at": datetime.utcnow(),
        }

        # Enviar via WhatsApp
        sent = await whatsapp_service.send_verification_code(phone, code)

        if sent:
            logger.info(f"Código de verificação WhatsApp enviado para {phone}")
        else:
            # Limpar código se falhou
            self._codes.pop(phone, None)

        return sent

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

        # Código correto - confirmar telefone
        user = await self._repository.find_by_phone(phone)
        if not user:
            logger.warning(f"Usuário não encontrado para telefone: {phone}")
            raise ValidationError("Usuário não encontrado")

        await self._repository.set_phone_confirmed(user.id)

        # Limpar código após confirmação bem-sucedida
        self._codes.pop(phone, None)

        logger.info(f"Telefone confirmado com sucesso: {phone}")
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
        # Em produção, implementar cooldown
        return True
