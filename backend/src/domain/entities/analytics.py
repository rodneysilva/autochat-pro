"""
Entidade Analytics/Metrics.

Armazena métricas e estatísticas de uso para bots e conversas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class MetricType(str, Enum):
    """Tipos de métricas coletadas."""

    MESSAGES_SENT = "messages_sent"
    MESSAGES_RECEIVED = "messages_received"
    CONVERSATIONS_STARTED = "conversations_started"
    CONVERSATIONS_CLOSED = "conversations_closed"
    AUTOMATION_RESPONSES = "automation_responses"
    LLM_RESPONSES = "llm_responses"
    AVG_RESPONSE_TIME = "avg_response_time"
    ACTIVE_USERS = "active_users"
    ERROR_RATE = "error_rate"


class PeriodType(str, Enum):
    """Períodos de agregação."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Analytics:
    """
    Entidade de Analytics/Métricas.

    Armazena métricas agregadas por período para bots e usuários.
    """

    bot_id: str
    metric_type: MetricType
    period: PeriodType
    value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "bot_id": self.bot_id,
            "metric_type": self.metric_type.value,
            "period": self.period.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class DailyStats:
    """
    Estatísticas diárias agregadas.

    Armazena resumo diário de todas as métricas para consultas rápidas.
    """

    bot_id: str
    date: datetime
    messages_sent: int = 0
    messages_received: int = 0
    conversations_started: int = 0
    conversations_closed: int = 0
    automation_responses: int = 0
    llm_responses: int = 0
    avg_response_time: float = 0.0
    active_users: int = 0
    errors: int = 0
    id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "bot_id": self.bot_id,
            "date": self.date.strftime("%Y-%m-%d") if self.date else None,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "conversations_started": self.conversations_started,
            "conversations_closed": self.conversations_closed,
            "automation_responses": self.automation_responses,
            "llm_responses": self.llm_responses,
            "avg_response_time": self.avg_response_time,
            "active_users": self.active_users,
            "errors": self.errors,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def total_conversations(self) -> int:
        """Total de conversas ativas (iniciadas - encerradas)."""
        return self.conversations_started - self.conversations_closed

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso (mensagens enviadas / total)."""
        total = self.messages_sent + self.errors
        return (self.messages_sent / total * 100) if total > 0 else 0.0
