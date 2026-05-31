"""
DTOs para casos de uso de autenticação.

Define as estruturas de dados para entrada e saída das operações
de registro, login e gerenciamento de autenticação.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ========================================
# Request DTOs
# ========================================

class RegisterRequest(BaseModel):
    """Dados para registro de novo usuário."""

    email: EmailStr = Field(..., description="Email do usuário")
    phone: Optional[str] = Field(None, description="Telefone do usuário")
    password: str = Field(..., min_length=8, description="Senha (mínimo 8 caracteres)")
    name: str = Field(..., min_length=2, description="Nome completo")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "phone": "+5511999999999",
                "password": "securepassword123",
                "name": "John Doe"
            }
        }


class LoginRequest(BaseModel):
    """Dados para login."""

    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Dados para refresh do token."""

    refresh_token: str = Field(..., description="Token de refresh")


class ConfirmEmailRequest(BaseModel):
    """Dados para confirmação de email."""

    token: str = Field(..., description="Token de confirmação")


class ConfirmPhoneRequest(BaseModel):
    """Dados para confirmação de telefone."""

    phone: str = Field(..., description="Telefone")
    code: str = Field(..., min_length=6, max_length=6, description="Código de verificação")


class ForgotPasswordRequest(BaseModel):
    """Dados para recuperação de senha."""

    email: EmailStr = Field(..., description="Email do usuário")


class ResetPasswordRequest(BaseModel):
    """Dados para reset de senha."""

    token: str = Field(..., description="Token de reset")
    new_password: str = Field(..., min_length=8, description="Nova senha")


# ========================================
# Response DTOs
# ========================================

class AuthResponse(BaseModel):
    """Resposta padrão de autenticação."""

    access_token: str = Field(..., description="Token de acesso JWT")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")


class UserResponse(BaseModel):
    """Dados do usuário para resposta."""

    id: str = Field(..., description="ID do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    name: str = Field(..., description="Nome do usuário")
    phone: Optional[str] = Field(None, description="Telefone do usuário")
    avatar: Optional[str] = Field(None, description="URL do avatar")
    email_confirmed: bool = Field(default=False, description="Email confirmado")
    phone_confirmed: bool = Field(default=False, description="Telefone confirmado")

    plan_type: str = Field(..., description="Tipo do plano")
    plan_max_bots: int = Field(..., description="Máximo de bots permitidos")

    created_at: str = Field(..., description="Data de criação")


class RegisterResponse(BaseModel):
    """Resposta do registro."""

    message: str = Field(..., description="Mensagem de sucesso")
    user: UserResponse = Field(..., description="Dados do usuário criado")


class LoginResponse(BaseModel):
    """Resposta do login."""

    message: str = Field(..., description="Mensagem de sucesso")
    access_token: str = Field(..., description="Token de acesso")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    user: UserResponse = Field(..., description="Dados do usuário")
