"""
DTOs para regras de automação.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ========================================
# Condition / Action sub-DTOs
# ========================================

class CondicaoRequest(BaseModel):
    """DTO para condição de regra."""
    tipo: str = Field("keyword", description="Tipo: keyword, regex, time, intent, has_media")
    campo: str = Field("message.content", description="Campo do contexto")
    operador: str = Field("contains", description="Operador: contains, equals, starts_with, ends_with, regex_match")
    valor: str = Field("", description="Valor de comparação")
    negar: bool = Field(False, description="Inverter resultado")


class AcaoRequest(BaseModel):
    """DTO para ação de regra."""
    tipo: str = Field("reply", description="Tipo: reply, forward, llm, tag, close, assign_human")
    delay: int = Field(0, ge=0, description="Delay em segundos")
    conteudo: str = Field("", description="Conteúdo da ação")
    parametros: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros extras")


# ========================================
# Request DTOs
# ========================================

class CriarRegraRequest(BaseModel):
    """DTO para criação de regra de automação."""
    bot_id: str = Field(..., description="ID do bot")
    nome: str = Field(..., min_length=2, max_length=100, description="Nome da regra")
    descricao: Optional[str] = Field("", max_length=500, description="Descrição")
    condicoes: List[CondicaoRequest] = Field(default_factory=list, description="Condições")
    acoes: List[AcaoRequest] = Field(default_factory=list, description="Ações")
    prioridade: int = Field(10, ge=1, le=100, description="Prioridade (1-100)")
    cooldown_seconds: int = Field(300, ge=0, description="Cooldown em segundos")
    ativa: bool = Field(True, description="Se está ativa")


class AtualizarRegraRequest(BaseModel):
    """DTO para atualização de regra de automação."""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    condicoes: Optional[List[CondicaoRequest]] = None
    acoes: Optional[List[AcaoRequest]] = None
    prioridade: Optional[int] = Field(None, ge=1, le=100)
    cooldown_seconds: Optional[int] = Field(None, ge=0)
    ativa: Optional[bool] = None


# ========================================
# Response DTOs
# ========================================

class CondicaoResponse(BaseModel):
    tipo: str
    campo: str
    operador: str
    valor: str
    negar: bool


class AcaoResponse(BaseModel):
    tipo: str
    delay: int
    conteudo: str
    parametros: Dict[str, Any]


class EstatisticasRegraResponse(BaseModel):
    total_execucoes: int
    ultima_execucao_em: Optional[datetime]


class RegraResponse(BaseModel):
    """DTO de resposta de regra de automação."""
    id: str
    bot_id: str
    nome: str
    descricao: str
    ativa: bool
    prioridade: int
    condicoes: List[CondicaoResponse]
    acoes: List[AcaoResponse]
    cooldown: int
    max_execucoes: Optional[int]
    limite_por_conversa: int
    estatisticas: EstatisticasRegraResponse
    criado_em: datetime
    atualizado_em: datetime


class ListaRegrasResponse(BaseModel):
    """DTO de lista de regras."""
    data: List[RegraResponse]
    total: int


# ========================================
# Helper: entity → response
# ========================================

def regra_to_response(rule) -> RegraResponse:
    """Converte entidade RegraAutomacao para RegraResponse DTO."""
    return RegraResponse(
        id=str(rule.id),
        bot_id=str(rule.bot_id),
        nome=rule.nome,
        descricao=rule.descricao,
        ativa=rule.ativado,
        prioridade=rule.prioridade,
        condicoes=[
            CondicaoResponse(
                tipo=c.tipo.value,
                campo=c.campo,
                operador=c.operador.value,
                valor=c.valor,
                negar=c.negar,
            )
            for c in rule.condicoes
        ],
        acoes=[
            AcaoResponse(
                tipo=a.tipo.value,
                delay=a.delay,
                conteudo=a.conteudo,
                parametros=a.parametros,
            )
            for a in rule.acoes
        ],
        cooldown=rule.cooldown,
        max_execucoes=rule.max_execucoes,
        limite_por_conversa=rule.limite_por_conversa,
        estatisticas=EstatisticasRegraResponse(
            total_execucoes=rule.estatisticas.total_execucoes,
            ultima_execucao_em=rule.estatisticas.ultima_execucao_em,
        ),
        criado_em=rule.criado_em,
        atualizado_em=rule.atualizado_em,
    )
