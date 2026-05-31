"""
DTOs para conversas e mensagens.

Data Transfer Objects para transferência de dados entre camadas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ========================================
# Request DTOs - Conversa
# ========================================

class AtribuirAtendenteRequest(BaseModel):
    """DTO para atribuir atendente."""

    usuario_id: UUID = Field(..., description="ID do atendente")


# ========================================
# Response DTOs - Conversa
# ========================================

class DadosClienteResponse(BaseModel):
    """DTO de dados do cliente."""

    id: str
    nome: str
    telefone: Optional[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextoConversaResponse(BaseModel):
    """DTO de contexto da conversa."""

    intent_atual: Optional[str]
    produto_atual: Optional[str]
    carrinho: List[Dict[str, Any]] = Field(default_factory=list)
    ultima_acao: Optional[str]


class ConversaResponse(BaseModel):
    """DTO de resposta de conversa."""

    id: UUID
    bot_id: UUID
    usuario_atendente_id: Optional[UUID]
    cliente: DadosClienteResponse
    status: str
    contexto: ContextoConversaResponse
    primeira_mensagem_em: Optional[datetime]
    ultima_mensagem_em: Optional[datetime]
    ultima_atividade_em: Optional[datetime]
    fechada_em: Optional[datetime]
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class ListaConversasResponse(BaseModel):
    """DTO de lista de conversas."""

    data: List[ConversaResponse]
    total: int
    pagina: int
    tamanho_pagina: int


# ========================================
# Request DTOs - Mensagem
# ========================================

class EnviarMensagemRequest(BaseModel):
    """DTO para envio de mensagem."""

    conversa_id: UUID = Field(..., description="ID da conversa")
    conteudo: str = Field(..., min_length=1, description="Conteúdo da mensagem")
    media_url: Optional[str] = Field(None, description="URL da mídia")


# ========================================
# Response DTOs - Mensagem
# ========================================

class MetadataMidiaResponse(BaseModel):
    """DTO de metadados de mídia."""

    mime_type: Optional[str]
    tamanho: Optional[int]
    duracao: Optional[int]
    legenda: Optional[str]


class MensagemResponse(BaseModel):
    """DTO de resposta de mensagem."""

    id: UUID
    conversa_id: UUID
    papel: str
    conteudo: str
    tipo: str
    media_url: Optional[str]
    media_metadata: Optional[MetadataMidiaResponse]
    provedor: str
    provedor_mensagem_id: Optional[str]
    status_entrega: str
    entregue_em: Optional[datetime]
    lida_em: Optional[datetime]
    criado_em: datetime

    model_config = {"from_attributes": True}


class ListaMensagensResponse(BaseModel):
    """DTO de lista de mensagens."""

    data: List[MensagemResponse]
    total: int
    pagina: int
    tamanho_pagina: int
