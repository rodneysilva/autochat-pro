"""
Domain entities module.
"""

from src.domain.entities.user import User, Plan, TipoPlano, StatusUsuario
from src.domain.entities.bot import Bot, BotType, BotStatus
from src.domain.entities.conversation import Conversation, ConversationStatus
from src.domain.entities.message import Message, MessageRole, MediaType
from src.domain.entities.automation_rule import AutomationRule
from src.domain.entities.analytics import Analytics, DailyStats, MetricType, PeriodType

__all__ = [
    "User",
    "Plan",
    "TipoPlano",
    "StatusUsuario",
    "Bot",
    "BotType",
    "BotStatus",
    "Conversation",
    "ConversationStatus",
    "Message",
    "MessageRole",
    "MediaType",
    "AutomationRule",
    "Analytics",
    "DailyStats",
    "MetricType",
    "PeriodType",
]
