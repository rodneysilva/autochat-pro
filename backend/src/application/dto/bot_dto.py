"""
DTOs para bots.

Data Transfer Objects para transferência de dados entre camadas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ========================================
# Request DTOs
# ========================================

class CriarBotRequest(BaseModel):
    """DTO para criação de bot."""

    nome: str = Field(..., min_length=2, max_length=100, description="Nome do bot")
    tipo: str = Field(..., description="Tipo do bot (whatsapp ou telegram)")
    mensagem_boas_vindas: Optional[str] = Field(
        None,
        description="Mensagem de boas-vindas"
    )
    mensagem_despedida: Optional[str] = Field(
        None,
        description="Mensagem de despedida"
    )


class AtualizarBotRequest(BaseModel):
    """DTO para atualização de bot."""

    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    mensagem_boas_vindas: Optional[str] = None
    mensagem_despedida: Optional[str] = None
    mensagem_resposta_padrao: Optional[str] = None

    # Working Hours
    working_hours_ativado: Optional[bool] = None
    working_hours_inicio: Optional[str] = None
    working_hours_fim: Optional[str] = None
    working_hours_timezone: Optional[str] = None
    working_hours_mensagem_fora: Optional[str] = None

    # LLM Config
    llm_ativado: Optional[bool] = None
    llm_provider: Optional[str] = None
    llm_modelo: Optional[str] = None
    llm_temperatura: Optional[float] = None
    llm_max_tokens: Optional[int] = None
    llm_system_prompt: Optional[str] = None
    llm_max_context_messages: Optional[int] = None


class ConfigurarWhatsAppRequest(BaseModel):
    """DTO para configuração de WhatsApp."""

    bot_token: Optional[str] = Field(None, description="Token do bot (Evolution API)")


class ConfigurarTelegramRequest(BaseModel):
    """DTO para configuração de Telegram."""

    bot_token: str = Field(..., description="Token do bot Telegram")


class TestarBotRequest(BaseModel):
    """DTO para teste de bot."""

    mensagem: str = Field(..., min_length=1, description="Mensagem de teste")


class CatalogoItemRequest(BaseModel):
    """DTO para item de catálogo."""

    id: str = Field(..., description="ID do produto")
    nome: str = Field(..., description="Nome do produto")
    descricao: str = Field(..., description="Descrição do produto")
    preco: float = Field(..., ge=0, description="Preço do produto")
    categoria: str = Field(..., description="Categoria do produto")
    imagem_url: Optional[str] = Field(None, description="URL da imagem")


class AtualizarCatalogoRequest(BaseModel):
    """DTO para atualização de catálogo."""

    ativado: bool = Field(..., description="Se o catálogo está ativado")
    itens: List[CatalogoItemRequest] = Field(..., description="Itens do catálogo")


# ========================================
# Response DTOs
# ========================================

class WorkingHoursResponse(BaseModel):
    ativado: bool
    inicio: str
    fim: str
    timezone: str
    mensagem_fora_horario: str


class LLMConfigResponse(BaseModel):
    ativado: bool
    provider: str = "glm"
    modelo: str
    temperatura: float
    max_tokens: int
    system_prompt: str
    fallback_para_llm: bool
    max_context_messages: int = 20


class CatalogoItemResponse(BaseModel):
    id: str
    nome: str
    descricao: str
    preco: float
    categoria: str
    imagem_url: Optional[str]


class CatalogoResponse(BaseModel):
    ativado: bool
    itens: List[CatalogoItemResponse]


class WhatsAppConfigResponse(BaseModel):
    numero_telefone: Optional[str]
    qr_code: Optional[str]
    profile_picture_url: Optional[str]


class TelegramConfigResponse(BaseModel):
    bot_username: Optional[str]
    webhook_url: Optional[str]


class EstatisticasBotResponse(BaseModel):
    total_mensagens: int
    total_conversas: int
    tempo_resposta_medio: float
    ultima_reset: Optional[datetime]


class BotResponse(BaseModel):
    """DTO de resposta de bot."""

    id: str
    usuario_id: str
    nome: str
    tipo: str
    status: str
    mensagem_boas_vindas: str
    mensagem_despedida: str
    mensagem_resposta_padrao: str
    working_hours: WorkingHoursResponse
    llm_config: LLMConfigResponse
    catalogo: CatalogoResponse
    whatsapp_config: Optional[WhatsAppConfigResponse] = None
    telegram_config: Optional[TelegramConfigResponse] = None
    estatisticas: EstatisticasBotResponse
    ultimo_erro: Optional[str]
    ultimo_conectado_em: Optional[datetime]
    criado_em: datetime
    atualizado_em: datetime


class ListaBotsResponse(BaseModel):
    """DTO de lista de bots."""

    data: List[BotResponse]
    total: int
    pagina: int
    tamanho_pagina: int


class QRCodeResponse(BaseModel):
    """DTO de resposta com QR Code."""

    status: str = Field(..., description="Status da conexão")
    qr_code: Optional[str] = Field(None, description="QR Code em base64")
    mensagem: Optional[str] = Field(None, description="Mensagem adicional")


class StatusConexaoResponse(BaseModel):
    """DTO de status de conexão."""

    status: str
    numero_telefone: Optional[str] = None
    conectado_em: Optional[datetime] = None
    ultimo_erro: Optional[str] = None


class TesteBotResponse(BaseModel):
    """DTO de resposta de teste."""

    mensagem_enviada: bool
    resposta: Optional[str] = None
    erro: Optional[str] = None


# ========================================
# Helper: Bot entity → BotResponse
# ========================================

def bot_to_response(bot) -> BotResponse:
    """Converte entidade Bot para BotResponse DTO."""
    return BotResponse(
        id=bot.id,
        usuario_id=bot.usuario_id,
        nome=bot.nome,
        tipo=bot.tipo.value if hasattr(bot.tipo, "value") else str(bot.tipo),
        status=bot.status.value if hasattr(bot.status, "value") else str(bot.status),
        mensagem_boas_vindas=bot.mensagem_boas_vindas,
        mensagem_despedida=bot.mensagem_despedida,
        mensagem_resposta_padrao=bot.mensagem_resposta_padrao,
        working_hours=WorkingHoursResponse(
            ativado=bot.working_hours.ativado,
            inicio=bot.working_hours.inicio,
            fim=bot.working_hours.fim,
            timezone=bot.working_hours.timezone,
            mensagem_fora_horario=bot.working_hours.mensagem_fora_horario,
        ),
        llm_config=LLMConfigResponse(
            ativado=bot.llm_config.ativado,
            provider=bot.llm_config.provider,
            modelo=bot.llm_config.modelo,
            temperatura=bot.llm_config.temperatura,
            max_tokens=bot.llm_config.max_tokens,
            system_prompt=bot.llm_config.system_prompt,
            fallback_para_llm=bot.llm_config.fallback_para_llm,
            max_context_messages=bot.llm_config.max_context_messages,
        ),
        catalogo=CatalogoResponse(
            ativado=bot.catalogo.ativado,
            itens=[
                CatalogoItemResponse(
                    id=item.id,
                    nome=item.nome,
                    descricao=item.descricao,
                    preco=item.preco,
                    categoria=item.categoria,
                    imagem_url=item.imagem_url,
                )
                for item in bot.catalogo.itens
            ],
        ),
        whatsapp_config=WhatsAppConfigResponse(
            numero_telefone=bot.whatsapp_config.numero_telefone,
            qr_code=bot.whatsapp_config.qr_code,
            profile_picture_url=bot.whatsapp_config.profile_picture_url,
        ),
        telegram_config=TelegramConfigResponse(
            bot_username=bot.telegram_config.bot_username,
            webhook_url=bot.telegram_config.webhook_url,
        ),
        estatisticas=EstatisticasBotResponse(
            total_mensagens=bot.estatisticas.total_mensagens,
            total_conversas=bot.estatisticas.total_conversas,
            tempo_resposta_medio=bot.estatisticas.tempo_resposta_medio,
            ultima_reset=bot.estatisticas.ultima_reset,
        ),
        ultimo_erro=bot.ultimo_erro,
        ultimo_conectado_em=bot.ultimo_conectado_em,
        criado_em=bot.criado_em,
        atualizado_em=bot.atualizado_em,
    )
