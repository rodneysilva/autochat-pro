"""
Endpoints de autenticação.

Define todos os endpoints relacionados a registro, login,
refresh de token e confirmação de conta.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field

from src.application.use_cases.register_use_case import RegisterUseCase
from src.application.use_cases.login_use_case import LoginUseCase
from src.application.use_cases.refresh_token_use_case import RefreshTokenUseCase
from src.application.use_cases.confirm_email_use_case import ConfirmEmailUseCase
from src.application.use_cases.password_reset_use_case import PasswordResetUseCase
from src.application.use_cases.confirm_phone_use_case import ConfirmPhoneUseCase
from src.api.middleware.auth import get_current_user
from src.application.dto.auth_dto import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    AuthResponse,
    UserResponse,
)
from src.shared.exceptions import BaseAppException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticação"])

security = HTTPBearer(auto_error=False)


# ========================================
# Request/Response Models
# ========================================

class ConfirmEmailRequest(BaseModel):
    """Request para confirmação de email."""
    token: str


class ResendConfirmationRequest(BaseModel):
    """Request para reenviar confirmação."""
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    """Request para recuperação de senha."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request para reset de senha."""
    token: str
    new_password: str = Field(..., min_length=8, description="Nova senha (mínimo 8 caracteres)")


class SendPhoneCodeRequest(BaseModel):
    """Request para enviar código de verificação SMS."""
    phone: str = Field(..., description="Número de telefone com DDI (+55...)")


class VerifyPhoneCodeRequest(BaseModel):
    """Request para verificar código SMS."""
    phone: str = Field(..., description="Número de telefone")
    code: str = Field(..., min_length=6, max_length=6, description="Código de 6 dígitos")


# ========================================
# Dependencies
# ========================================

async def get_register_use_case() -> RegisterUseCase:
    """Obtém instância do RegisterUseCase."""
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.user_repository_impl import MongoUserRepository

    await MongoDB.connect()
    repository = MongoUserRepository(MongoDB.get_database())
    return RegisterUseCase(repository)


async def get_login_use_case() -> LoginUseCase:
    """Obtém instância do LoginUseCase."""
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.user_repository_impl import MongoUserRepository

    await MongoDB.connect()
    repository = MongoUserRepository(MongoDB.get_database())
    return LoginUseCase(repository)


async def get_refresh_use_case() -> RefreshTokenUseCase:
    """Obtém instância do RefreshTokenUseCase."""
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.user_repository_impl import MongoUserRepository

    await MongoDB.connect()
    repository = MongoUserRepository(MongoDB.get_database())
    return RefreshTokenUseCase(repository)


async def get_confirm_email_use_case() -> ConfirmEmailUseCase:
    """Obtém instância do ConfirmEmailUseCase."""
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.user_repository_impl import MongoUserRepository

    await MongoDB.connect()
    repository = MongoUserRepository(MongoDB.get_database())
    return ConfirmEmailUseCase(repository)


# ========================================
# Endpoints
# ========================================

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário.",
)
async def register(
    request: RegisterRequest,
    use_case: RegisterUseCase = Depends(get_register_use_case),
    confirm_use_case: ConfirmEmailUseCase = Depends(get_confirm_email_use_case),
):
    """
    Endpoint de registro.

    Cria um novo usuário com os dados fornecidos.
    Um email de confirmação será enviado para o usuário.
    """
    try:
        result = await use_case.execute(request)

        # Gerar token de confirmação e enviar email
        try:
            from src.infrastructure.external_services.email import get_email_service

            confirm_token = confirm_use_case.generate_confirmation_token(str(result.user.id))
            confirm_link = confirm_use_case.generate_confirmation_link(confirm_token)

            email_service = get_email_service()
            await email_service.send_confirmation_email(
                to_email=result.user.email,
                user_name=result.user.nome,
                confirmation_link=confirm_link,
            )
        except Exception as e:
            logger.error(f"Erro ao enviar email de confirmação: {e}")
            # Não falhar o registro se o email falhar

        return result
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"Erro não tratado em register: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro interno do servidor"}}
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login",
    description="Autentica um usuário e retorna tokens JWT.",
)
async def login(
    request: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
):
    """
    Endpoint de login.

    Autentica o usuário com email e senha,
    retornando um par de tokens JWT (access + refresh).
    """
    try:
        return await use_case.execute(request)
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"Erro não tratado em login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro interno do servidor"}}
        )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh token",
    description="Renova o token de acesso usando o token de refresh.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_use_case),
):
    """
    Endpoint de refresh.

    Renova o token de acesso utilizando um token de refresh válido.
    """
    try:
        return await use_case.execute(request.refresh_token)
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"Erro não tratado em refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro interno do servidor"}}
        )


@router.post(
    "/logout",
    summary="Logout",
    description="Logout do usuário (invalida o token).",
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Endpoint de logout.

    Invalida o token atual (implementação futura com blacklist).
    """
    # TODO: Implementar blacklist de tokens no Redis
    return {"message": "Logout realizado com sucesso"}


@router.get(
    "/me",
    summary="Dados do usuário autenticado",
    description="Retorna os dados do usuário autenticado.",
)
async def get_current_user_endpoint(
    current_user = Depends(get_current_user),
):
    """
    Endpoint para obter dados do usuário autenticado.

    Requer token de acesso válido.
    """
    from src.domain.entities.user import Usuario

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        nome=current_user.nome,
        telefone=current_user.telefone,
        avatar=current_user.avatar,
        email_confirmado=current_user.email_confirmado,
        telefone_confirmado=current_user.telefone_confirmado,
        plano_tipo=current_user.plano.tipo.value if hasattr(current_user.plano.tipo, 'value') else current_user.plano.tipo,
        plano_max_bots=current_user.plano.max_bots,
        criado_em=current_user.criado_em.isoformat() if current_user.criado_em else "",
    )


@router.post(
    "/confirm-email",
    summary="Confirmar email",
    description="Confirma o email do usuário usando o token enviado por email.",
)
async def confirm_email(
    request: ConfirmEmailRequest,
    use_case: ConfirmEmailUseCase = Depends(get_confirm_email_use_case),
):
    """
    Endpoint de confirmação de email.

    Valida o token e marca o email como confirmado.
    """
    try:
        success = await use_case.confirm_email(request.token)

        if success:
            # Enviar email de boas-vindas
            try:
                from src.infrastructure.external_services.email import get_email_service
                from src.infrastructure.repositories.user_repository_impl import MongoUserRepository
                from src.infrastructure.database.mongodb import MongoDB

                # Buscar usuário para enviar email
                repository = MongoUserRepository(MongoDB.get_database())

                # Obter user_id do token
                import jwt
                from src.shared.config import settings
                payload = jwt.decode(
                    request.token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM]
                )
                user = await repository.find_by_id(payload["sub"])

                if user:
                    email_service = get_email_service()
                    await email_service.send_welcome_email(
                        to_email=user.email,
                        user_name=user.nome,
                    )
            except Exception as e:
                logger.error(f"Erro ao enviar email de boas-vindas: {e}")

        return {"message": "Email confirmado com sucesso"}
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"Erro não tratado em confirm_email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro interno do servidor"}}
        )


@router.post(
    "/resend-confirmation",
    summary="Reenviar email de confirmação",
    description="Reenvia o email de confirmação para o usuário.",
)
async def resend_confirmation(
    request: ResendConfirmationRequest,
    use_case: ConfirmEmailUseCase = Depends(get_confirm_email_use_case),
):
    """
    Endpoint para reenviar confirmação de email.

    Envia um novo email de confirmação.
    """
    try:
        from src.infrastructure.database.mongodb import MongoDB
        from src.infrastructure.repositories.user_repository_impl import MongoUserRepository
        from src.infrastructure.external_services.email import get_email_service

        repository = MongoUserRepository(MongoDB.get_database())
        user = await repository.find_by_email(request.email)

        if not user:
            # Não revelar se o email existe
            return {"message": "Se o email estiver cadastrado, uma nova confirmação será enviada"}

        if user.email_confirmado:
            return {"message": "Email já confirmado"}

        # Gerar novo token e enviar email
        confirm_token = use_case.generate_confirmation_token(str(user.id))
        confirm_link = use_case.generate_confirmation_link(confirm_token)

        email_service = get_email_service()
        await email_service.send_confirmation_email(
            to_email=user.email,
            user_name=user.nome,
            confirmation_link=confirm_link,
        )

        logger.info(f"Email de confirmação reenviado para: {user.email}")
        return {"message": "Email de confirmação reenviado"}

    except Exception as e:
        logger.error(f"Erro não tratado em resend_confirmation: {e}")
        # Retornar sucesso mesmo com erro para não revelar informações
        return {"message": "Processamento concluído"}


# ========================================
# Password Reset Endpoints
# ========================================

async def get_password_reset_use_case() -> PasswordResetUseCase:
    """Obtém instância do PasswordResetUseCase."""
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.user_repository_impl import MongoUserRepository

    await MongoDB.connect()
    repository = MongoUserRepository(MongoDB.get_database())
    return PasswordResetUseCase(repository)


@router.post(
    "/forgot-password",
    summary="Esqueci minha senha",
    description="Envia um email com link para redefinir a senha.",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    use_case: PasswordResetUseCase = Depends(get_password_reset_use_case),
):
    """
    Endpoint para iniciar recuperação de senha.

    Envia um email com link de reset.
    """
    try:
        # Gerar token
        reset_token = use_case.generate_reset_token(request.email)
        reset_link = use_case.generate_reset_link(reset_token)

        # Enviar email
        await use_case.send_reset_email(request.email, reset_link)

        return {"message": "Se o email estiver cadastrado, você receberá um link para redefinir sua senha"}
    except Exception as e:
        logger.error(f"Erro não tratado em forgot_password: {e}")
        # Retornar sucesso mesmo com erro para não revelar informações
        return {"message": "Processamento concluído"}


@router.post(
    "/reset-password",
    summary="Redefinir senha",
    description="Redefine a senha usando o token enviado por email.",
)
async def reset_password(
    request: ResetPasswordRequest,
    use_case: PasswordResetUseCase = Depends(get_password_reset_use_case),
):
    """
    Endpoint para redefinir senha.

    Valida o token e atualiza a senha.
    """
    try:
        await use_case.reset_password(request.token, request.new_password)
        return {"message": "Senha redefinida com sucesso"}
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"Erro não tratado em reset_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro interno do servidor"}}
        )


# ========================================
# Phone Confirmation Endpoints
# ========================================

async def get_confirm_phone_use_case() -> ConfirmPhoneUseCase:
    """Obtém instância do ConfirmPhoneUseCase."""
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.user_repository_impl import MongoUserRepository

    await MongoDB.connect()
    repository = MongoUserRepository(MongoDB.get_database())
    return ConfirmPhoneUseCase(repository)


@router.post(
    "/send-phone-code",
    summary="Enviar código de verificação SMS",
    description="Envia um código de 6 dígitos por SMS para confirmar o telefone.",
)
async def send_phone_code(
    request: SendPhoneCodeRequest,
    use_case: ConfirmPhoneUseCase = Depends(get_confirm_phone_use_case),
):
    """
    Endpoint para enviar código de verificação por SMS.

    Envia um SMS com código de 6 dígitos.
    """
    try:
        # Verificar se pode reenviar
        if not use_case.can_resend(request.phone):
            return {"message": "Aguarde 1 minuto para solicitar um novo código"}

        sent = await use_case.send_verification_code(request.phone)

        if sent:
            return {"message": "Código de verificação enviado"}
        else:
            return {"message": "Não foi possível enviar o SMS. Tente novamente mais tarde"}

    except Exception as e:
        logger.error(f"Erro não tratado em send_phone_code: {e}")
        return {"message": "Erro ao processar solicitação"}


@router.post(
    "/verify-phone",
    summary="Verificar código SMS",
    description="Verifica o código enviado por SMS e confirma o telefone.",
)
async def verify_phone(
    request: VerifyPhoneCodeRequest,
    use_case: ConfirmPhoneUseCase = Depends(get_confirm_phone_use_case),
):
    """
    Endpoint para verificar código de telefone.

    Valida o código e marca o telefone como confirmado.
    """
    try:
        await use_case.verify_code(request.phone, request.code)
        return {"message": "Telefone confirmado com sucesso"}
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"Erro não tratado em verify_phone: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro interno do servidor"}}
        )
