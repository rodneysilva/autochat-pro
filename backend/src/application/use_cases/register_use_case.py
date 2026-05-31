"""
Caso de uso de registro de novo usuário.

Implementa a lógica de negócio para criação de novos usuários,
incluindo validações e preparação dos dados.
"""

from typing import Optional

from src.domain.entities.user import User, Plan, UserStatus
from src.domain.repositories.user_repository import UserRepository
from src.application.dto.auth_dto import RegisterRequest, RegisterResponse, UserResponse
from src.application.services.password_service import PasswordService
from src.shared.exceptions import ValidationError
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class RegisterUseCase:
    """Caso de uso para registro de usuários."""

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa o caso de uso.

        Args:
            user_repository: Repositório de usuários.
        """
        self._repository = user_repository

    async def execute(self, request: RegisterRequest) -> RegisterResponse:
        """
        Executa o registro de um novo usuário.

        Args:
            request: Dados do registro.

        Returns:
            Resposta com os dados do usuário criado.

        Raises:
            ValidationError: Se os dados forem inválidos ou o email já existir.
        """
        logger.info(f"Tentativa de registro: {request.email}")

        # Verificar se o email já existe
        if await self._repository.email_exists(request.email):
            logger.warning(f"Email já cadastrado: {request.email}")
            raise ValidationError(
                "Já existe uma conta com este email",
                field="email"
            )

        # Verificar se o telefone já existe (se fornecido)
        if request.phone:
            phone_clean = self._clean_phone(request.phone)
            if await self._repository.phone_exists(phone_clean):
                logger.warning(f"Telefone já cadastrado: {phone_clean}")
                raise ValidationError(
                    "Já existe uma conta com este telefone",
                    field="phone"
                )

        # Hash da senha
        password_hash = PasswordService.hash_password(request.password)

        # Criar entidade do usuário
        user = User(
            email=request.email,
            phone=phone_clean if request.phone else None,
            password_hash=password_hash,
            name=request.name,
            email_confirmed=False,  # Requer confirmação por email
            phone_confirmed=False,
            plan=Plan(type="free"),  # Plano free por padrão
            status=UserStatus.ACTIVE,
        )

        # Salvar no banco
        created_user = await self._repository.create(user)

        logger.info(f"Usuário registrado com sucesso: {created_user.email}")

        # TODO: Enviar email de confirmação
        # await self._send_confirmation_email(created_user)

        return self._to_response(created_user)

    def _clean_phone(self, phone: str) -> str:
        """
        Limpa e formata o número de telefone.

        Args:
            phone: Telefone bruto.

        Returns:
            Telefone limpo.
        """
        # Remove caracteres não numéricos
        return "".join(filter(str.isdigit, phone))

    def _to_response(self, user: User) -> RegisterResponse:
        """
        Converte a entidade User para RegisterResponse.

        Args:
            user: Entidade do usuário.

        Returns:
            Response DTO.
        """
        return RegisterResponse(
            message="Usuário registrado com sucesso. Verifique seu email para confirmar a conta.",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                phone=user.phone,
                avatar=user.avatar,
                email_confirmed=user.email_confirmed,
                phone_confirmed=user.phone_confirmed,
                plan_type=user.plan.type,
                plan_max_bots=user.plan.max_bots,
                created_at=user.created_at.isoformat() if user.created_at else "",
            )
        )
