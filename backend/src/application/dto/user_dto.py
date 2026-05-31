"""
DTOs para usuários.

Data Transfer Objects para transferência de dados entre camadas.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ========================================
# Request DTOs
# ========================================

class RegistroRequest(BaseModel):
    """DTO para registro de novo usuário."""

    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., min_length=8, description="Senha do usuário")
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do usuário")
    telefone: Optional[str] = Field(None, description="Telefone do usuário")

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        """Valida se a senha é forte."""
        if not any(c.isupper() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")
        if not any(c.islower() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter pelo menos um número")
        return v


class LoginRequest(BaseModel):
    """DTO para login."""

    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., description="Senha do usuário")


class ConfirmarEmailRequest(BaseModel):
    """DTO para confirmação de email."""

    token: str = Field(..., description="Token de confirmação")
    codigo: Optional[str] = Field(None, description="Código de confirmação (6 dígitos)")


class ConfirmarTelefoneRequest(BaseModel):
    """DTO para confirmação de telefone."""

    telefone: str = Field(..., description="Telefone do usuário")
    codigo: str = Field(..., min_length=6, max_length=6, description="Código de confirmação")


class ReenviarConfirmacaoRequest(BaseModel):
    """DTO para reenviar confirmação."""


class EsqueciSenhaRequest(BaseModel):
    """DTO para solicitação de recuperação de senha."""

    email: EmailStr = Field(..., description="Email do usuário")


class RedefinirSenhaRequest(BaseModel):
    """DTO para redefinição de senha."""

    token: str = Field(..., description="Token de redefinição")
    senha: str = Field(..., min_length=8, description="Nova senha")


class RefreshTokenRequest(BaseModel):
    """DTO para refresh token."""

    refresh_token: str = Field(..., description="Token de refresh")


class AtualizarUsuarioRequest(BaseModel):
    """DTO para atualização de usuário."""

    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar: Optional[str] = Field(None, description="URL do avatar")


class AlterarSenhaRequest(BaseModel):
    """DTO para alteração de senha."""

    senha_atual: str = Field(..., description="Senha atual")
    nova_senha: str = Field(..., min_length=8, description="Nova senha")


# ========================================
# Response DTOs
# ========================================

class ConfiguracaoPlanoResponse(BaseModel):
    """DTO de configuração de plano."""

    tipo: str = Field(..., description="Tipo do plano")
    max_bots: int = Field(..., description="Máximo de bots permitidos")
    max_mensagens_por_mes: int = Field(..., description="Máximo de mensagens por mês")
    max_contatos: int = Field(..., description="Máximo de contatos")
    features: List[str] = Field(default_factory=list, description="Features do plano")
    expira_em: Optional[datetime] = Field(None, description="Data de expiração")
    trial_termina_em: Optional[datetime] = Field(None, description="Data final do trial")
    trial_utilizado: bool = Field(default=False, description="Se o trial foi utilizado")


class UsuarioResponse(BaseModel):
    """DTO de resposta de usuário."""

    id: UUID = Field(..., description="ID do usuário")
    email: str = Field(..., description="Email do usuário")
    nome: str = Field(..., description="Nome do usuário")
    telefone: Optional[str] = Field(None, description="Telefone do usuário")
    email_confirmado: bool = Field(..., description="Se o email foi confirmado")
    telefone_confirmado: bool = Field(..., description="Se o telefone foi confirmado")
    avatar: Optional[str] = Field(None, description="URL do avatar")
    plano: ConfiguracaoPlanoResponse = Field(..., description="Configuração do plano")
    criado_em: datetime = Field(..., description="Data de criação")

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """DTO de resposta de token."""

    access_token: str = Field(..., description="Token de acesso")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    usuario: UsuarioResponse = Field(..., description="Dados do usuário")


class RefreshTokenResponse(BaseModel):
    """DTO de resposta de refresh token."""

    access_token: str = Field(..., description="Novo token de acesso")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")


class MensagemResponse(BaseModel):
    """DTO de resposta genérica com mensagem."""

    mensagem: str = Field(..., description="Mensagem de sucesso ou informação")


class PaginatedResponse(BaseModel):
    """DTO de resposta paginada."""

    total: int = Field(..., description="Total de itens")
    pagina: int = Field(..., description="Página atual")
    tamanho_pagina: int = Field(..., description="Tamanho da página")
    total_paginas: int = Field(..., description="Total de páginas")
