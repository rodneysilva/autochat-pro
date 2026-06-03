"""
Configuração central da aplicação.

Este módulo utiliza Pydantic Settings para gerenciar todas as variáveis de ambiente
e configurações da aplicação de forma type-safe.
"""

from functools import lru_cache
from typing import List, Optional
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações globais da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ========================================
    # Ambiente
    # ========================================
    ENVIRONMENT: str = Field(default="development", description="Ambiente da aplicação")
    DEBUG: bool = Field(default=False, description="Modo debug")
    API_V1_PREFIX: str = Field(default="/api/v1", description="Prefixo da API v1")

    # ========================================
    # Servidor
    # ========================================
    HOST: str = Field(default="0.0.0.0", description="Host do servidor")
    PORT: int = Field(default=8000, description="Porta do servidor")

    # ========================================
    # Segurança
    # ========================================
    SECRET_KEY: str = Field(..., description="Chave secreta para JWT (OBRIGATÓRIO)")
    ALGORITHM: str = Field(default="HS256", description="Algoritmo de assinatura JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=480,
        description="Tempo de expiração do access token em minutos"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Tempo de expiração do refresh token em dias"
    )

    # ========================================
    # MongoDB
    # ========================================
    MONGODB_URL: str = Field(default="mongodb://mongodb:27017", description="URL do MongoDB")
    DATABASE_NAME: str = Field(default="autochat_pro", description="Nome do banco de dados")

    @property
    def mongodb_db_name(self) -> str:
        """Nome do banco de dados MongoDB."""
        return self.DATABASE_NAME

    # ========================================
    # Redis
    # ========================================
    REDIS_URL: str = Field(default="redis://redis:6379/0", description="URL do Redis")

    # ========================================
    # CORS
    # ========================================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Origens permitidas para CORS"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins de string para lista."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.strip("[]").split(",")]
        return v

    # ========================================
    # Email
    # ========================================
    MAIL_USERNAME: str = Field(default="", description="Usuário do servidor de email")
    MAIL_PASSWORD: str = Field(default="", description="Senha do servidor de email")
    MAIL_FROM: str = Field(default="noreply@autochat.pro", description="Email remetente")
    MAIL_PORT: int = Field(default=587, description="Porta do servidor SMTP")
    MAIL_SERVER: str = Field(default="postfix", description="Servidor SMTP")
    MAIL_FROM_NAME: str = Field(default="AutoChat Pro", description="Nome do remetente")
    MAIL_STARTTLS: bool = Field(default=True, description="Usar STARTTLS")
    MAIL_SSL_TLS: bool = Field(default=False, description="Usar SSL/TLS")

    # ========================================
    # SMS (Twilio)
    # ========================================
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, description="Account SID do Twilio")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, description="Auth Token do Twilio")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None, description="Número de telefone do Twilio")

    # ========================================
    # LLM - GLM (provider padrão)
    # ========================================
    LLM_API_URL: Optional[str] = Field(default=None, description="URL da API do LLM")
    LLM_API_KEY: Optional[str] = Field(default=None, description="API Key do LLM")
    LLM_MODEL: str = Field(default="glm-4", description="Modelo LLM padrão")
    LLM_TEMPERATURE: float = Field(default=0.7, description="Temperatura padrão do LLM")
    LLM_MAX_TOKENS: int = Field(default=2048, description="Máximo de tokens padrão")

    # ========================================
    # LLM - OpenAI
    # ========================================
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="API Key do OpenAI")

    # ========================================
    # LLM - Anthropic
    # ========================================
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="API Key do Anthropic")

    # ========================================
    # LLM - Ollama (local)
    # ========================================
    OLLAMA_URL: str = Field(default="http://localhost:11434", description="URL do Ollama")

    # ========================================
    # Telegram
    # ========================================
    TELEGRAM_WEBHOOK_BASE_URL: str = Field(
        default="",
        description="URL base para webhooks do Telegram (ex: https://autochat.rodney.website)"
    )

    # ========================================
    # WhatsApp
    # ========================================
    WHATSAPP_API_URL: str = Field(default="http://evolution-api:8080", description="URL da API do WhatsApp")
    WHATSAPP_API_KEY: str = Field(
        default="change-me-in-production",
        description="API Key do WhatsApp (OBRIGATÓRIO em produção)"
    )

    # ========================================
    # Rate Limiting
    # ========================================
    RATE_LIMIT_FREE: int = Field(default=100, description="Limite de requisições por minuto (Free)")
    RATE_LIMIT_BASIC: int = Field(default=300, description="Limite de requisições por minuto (Basic)")
    RATE_LIMIT_PRO: int = Field(default=1000, description="Limite de requisições por minuto (Pro)")

    # ========================================
    # Planos
    # ========================================
    TRIAL_DAYS: int = Field(default=14, description="Dias de trial gratuito")

    # ========================================
    # Frontend
    # ========================================
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="URL do frontend")

    # ========================================
    # Logging
    # ========================================
    LOG_LEVEL: str = Field(default="INFO", description="Nível de log")

    @property
    def is_production(self) -> bool:
        """Verifica se está em produção."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento."""
        return self.ENVIRONMENT == "development"

    @property
    def database_url(self) -> str:
        """URL completa do banco de dados."""
        return self.MONGODB_URL

    def validate_production(self) -> None:
        """Valida configurações obrigatórias para produção."""
        if self.is_production:
            if self.SECRET_KEY in ["autochat-secret-key-development-mudar-em-producao", "change-me"]:
                raise ValueError("SECRET_KEY deve ser alterado em produção")
            if self.WHATSAPP_API_KEY == "change-me-in-production":
                raise ValueError("WHATSAPP_API_KEY deve ser configurado em produção")


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância cacheada das configurações.

    Utiliza lru_cache para garantir que as configurações sejam carregadas
    apenas uma vez e reutilizadas durante toda a aplicação.
    """
    settings = Settings()
    settings.validate_production()
    return settings


# Instância global das configurações
settings = get_settings()
