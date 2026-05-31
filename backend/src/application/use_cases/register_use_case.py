"""
Caso de uso de registro de novo usuário.

Implementa a lógica de negócio para criação de novos usuários,
incluindo validações e preparação dos dados.
"""

from typing import Optional

from src.domain.entities.user import Usuario, ConfiguracaoPlano, StatusUsuario, TipoPlano
from src.domain.repositories.user_repository import UserRepository
from src.application.dto.auth_dto import RegisterRequest, RegisterResponse, UserResponse
from src.application.services.password_service import PasswordService
from src.shared.exceptions import ValidationException
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
            ValidationException: Se os dados forem inválidos ou o email já existir.
        """
        logger.info(f"Tentativa de registro: {request.email}")

        # Verificar se o email já existe
        if await self._repository.email_exists(request.email):
            logger.warning(f"Email já cadastrado: {request.email}")
            raise ValidationException(
                "Já existe uma conta com este email",
                field="email"
            )

        # Verificar se o telefone já existe (se fornecido)
        if request.phone:
            phone_clean = self._clean_phone(request.phone)
            if await self._repository.phone_exists(phone_clean):
                logger.warning(f"Telefone já cadastrado: {phone_clean}")
                raise ValidationException(
                    "Já existe uma conta com este telefone",
                    field="phone"
                )

        # Hash da senha
        password_hash = PasswordService.hash_password(request.password)

        # Criar entidade do usuário
        plano = ConfiguracaoPlano(tipo=TipoPlano.FREE)
        plano._aplicar_limites()

        user = Usuario(
            email=request.email,
            telefone=phone_clean if request.phone else None,
            senha_hash=password_hash,
            nome=request.name,
            email_confirmado=False,  # Requer confirmação por email
            telefone_confirmado=False,
            plano=plano,
            status=StatusUsuario.ATIVO,
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

    def _to_response(self, user: Usuario) -> RegisterResponse:
        """
        Converte a entidade Usuario para RegisterResponse.

        Args:
            user: Entidade do usuário.

        Returns:
            Response DTO.
        """
        return RegisterResponse(
            message="Usuário registrado com sucesso. Verifique seu email para confirmar a conta.",
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                nome=user.nome,
                telefone=user.telefone,
                avatar=user.avatar,
                email_confirmado=user.email_confirmado,
                telefone_confirmado=user.telefone_confirmado,
                plano_tipo=user.plano.tipo.value if hasattr(user.plano.tipo, 'value') else user.plano.tipo,
                plano_max_bots=user.plano.max_bots,
                criado_em=user.criado_em.isoformat() if user.criado_em else "",
            )
        )
