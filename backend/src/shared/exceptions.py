"""
Exceções customizadas da aplicação.

Este módulo define todas as exceções específicas do domínio da aplicação,
seguindo o princípio de criar exceções ricas em contexto.
"""

from typing import Any, Optional

from fastapi import HTTPException, status


class BaseAppException(Exception):
    """
    Exceção base da aplicação.

    Todas as exceções customizadas devem herdar desta classe.
    Fornece contexto adicional e mensagem amigável.
    """

    def __init__(
        self,
        message: str,
        code: str = "ERROR",
        details: Optional[dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

    def to_http_exception(self) -> HTTPException:
        """Converte para HTTPException do FastAPI."""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "error": {
                    "code": self.code,
                    "message": self.message,
                    "details": self.details,
                }
            },
        )


# ========================================
# Exceções de Domínio
# ========================================

class DomainException(BaseAppException):
    """Exceção base para erros de domínio."""

    def __init__(
        self,
        message: str,
        code: str = "DOMAIN_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class EntityNotFoundException(DomainException):
    """Exceção levantada quando uma entidade não é encontrada."""

    def __init__(
        self,
        entity_name: str,
        entity_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"{entity_name} não encontrado(a)"
        if entity_id:
            message += f" (ID: {entity_id})"

        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            details=details or {"entity": entity_name, "id": entity_id},
        )


class EntityAlreadyExistsException(DomainException):
    """Exceção levantada quando tenta criar uma entidade que já existe."""

    def __init__(
        self,
        entity_name: str,
        field: str,
        value: str,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"{entity_name} com {field} '{value}' já existe"

        super().__init__(
            message=message,
            code="ENTITY_ALREADY_EXISTS",
            details=details or {"entity": entity_name, "field": field, "value": value},
        )


class ValidationException(DomainException):
    """Exceção levantada quando há erro de validação."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details or {"field": field} if field else details,
        )


class BusinessRuleException(DomainException):
    """Exceção levantada quando uma regra de negócio é violada."""

    def __init__(
        self,
        message: str,
        rule_name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="BUSINESS_RULE_VIOLATION",
            details=details or {"rule": rule_name} if rule_name else details,
        )


# ========================================
# Exceções de Autenticação e Autorização
# ========================================

class AuthException(BaseAppException):
    """Exceção base para erros de autenticação."""

    def __init__(
        self,
        message: str,
        code: str = "AUTH_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidCredentialsException(AuthException):
    """Exceção levantada quando as credenciais são inválidas."""

    def __init__(self):
        super().__init__(
            message="Credenciais inválidas",
            code="INVALID_CREDENTIALS",
        )


class TokenExpiredException(AuthException):
    """Exceção levantada quando o token está expirado."""

    def __init__(self):
        super().__init__(
            message="Token expirado",
            code="TOKEN_EXPIRED",
        )


class InvalidTokenException(AuthException):
    """Exceção levantada quando o token é inválido."""

    def __init__(self):
        super().__init__(
            message="Token inválido",
            code="INVALID_TOKEN",
        )


class UnauthorizedException(AuthException):
    """Exceção levantada quando o usuário não tem permissão."""

    def __init__(self, resource: Optional[str] = None):
        message = "Não autorizado"
        if resource:
            message += f" para acessar {resource}"

        super().__init__(
            message=message,
            code="UNAUTHORIZED",
        )


class EmailNotConfirmedException(AuthException):
    """Exceção levantada quando o email não foi confirmado."""

    def __init__(self):
        super().__init__(
            message="Email não confirmado. Por favor, verifique seu email.",
            code="EMAIL_NOT_CONFIRMED",
        )


class PhoneNotConfirmedException(AuthException):
    """Exceção levantada quando o telefone não foi confirmado."""

    def __init__(self):
        super().__init__(
            message="Telefone não confirmado. Por favor, verifique seu SMS.",
            code="PHONE_NOT_CONFIRMED",
        )


# ========================================
# Exceções de Serviços Externos
# ========================================

class ExternalServiceException(BaseAppException):
    """Exceção base para erros de serviços externos."""

    def __init__(
        self,
        service_name: str,
        message: str = "Erro ao comunicar com serviço externo",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=f"{service_name}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            details=details or {"service": service_name},
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class EmailServiceException(ExternalServiceException):
    """Exceção levantada quando há erro no serviço de email."""

    def __init__(self, message: str = "Erro ao enviar email"):
        super().__init__(service_name="EmailService", message=message)


class SmsServiceException(ExternalServiceException):
    """Exceção levantada quando há erro no serviço de SMS."""

    def __init__(self, message: str = "Erro ao enviar SMS"):
        super().__init__(service_name="SmsService", message=message)


class LLMServiceException(ExternalServiceException):
    """Exceção levantada quando há erro no serviço de LLM."""

    def __init__(self, message: str = "Erro ao comunicar com LLM"):
        super().__init__(service_name="LLMService", message=message)


class WhatsAppServiceException(ExternalServiceException):
    """Exceção levantada quando há erro no serviço de WhatsApp."""

    def __init__(self, message: str = "Erro ao comunicar com WhatsApp"):
        super().__init__(service_name="WhatsAppService", message=message)


class TelegramServiceException(ExternalServiceException):
    """Exceção levantada quando há erro no serviço de Telegram."""

    def __init__(self, message: str = "Erro ao comunicar com Telegram"):
        super().__init__(service_name="TelegramService", message=message)


# ========================================
# Exceções de Limite/Quota
# ========================================

class LimitExceededException(BaseAppException):
    """Exceção levantada quando um limite é excedido."""

    def __init__(
        self,
        resource: str,
        limit: int,
        current: int,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"Limite de {resource} excedido ({current}/{limit})"

        super().__init__(
            message=message,
            code="LIMIT_EXCEEDED",
            details=details or {"resource": resource, "limit": limit, "current": current},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class PlanLimitExceededException(LimitExceededException):
    """Exceção levantada quando o limite do plano é excedido."""

    def __init__(
        self,
        resource: str,
        plan_type: str,
        limit: int,
        current: int,
    ):
        super().__init__(
            resource=resource,
            limit=limit,
            current=current,
            details={"plan": plan_type},
        )


class RateLimitExceededException(LimitExceededException):
    """Exceção levantada quando o rate limit é excedido."""

    def __init__(self, limit: int):
        super().__init__(
            resource="requisições",
            limit=limit,
            current=limit,
        )


# ========================================
# Exceções de Concorrência
# ========================================

class ConflictException(BaseAppException):
    """Exceção levantada quando há conflito de dados."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="CONFLICT",
            details=details,
            status_code=status.HTTP_409_CONFLICT,
        )


class ResourceLockedException(ConflictException):
    """Exceção levantada quando um recurso está bloqueado."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} {resource_id} está bloqueado",
            details={"resource": resource, "id": resource_id},
        )


# ========================================
# Aliases para compatibilidade
# ========================================
ValidationError = ValidationException
UnauthorizedError = AuthException
