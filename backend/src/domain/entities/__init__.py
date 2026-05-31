"""
Domain entities module.
"""

from src.domain.entities.user import Usuario, ConfiguracaoPlano, TipoPlano, StatusUsuario
from src.domain.entities.bot import Bot, TipoBot, StatusBot
from src.domain.entities.conversation import Conversa, StatusConversa, Mensagem, PapelMensagem, TipoMensagem
from src.domain.entities.automation_rule import RegraAutomacao, TipoCondicao, OperadorCondicao, TipoAcao, Condicao, Acao
from src.domain.entities.analytics import Analytics, DailyStats, MetricType, PeriodType

__all__ = [
    "Usuario",
    "ConfiguracaoPlano",
    "TipoPlano",
    "StatusUsuario",
    "Bot",
    "TipoBot",
    "StatusBot",
    "Conversa",
    "StatusConversa",
    "Mensagem",
    "PapelMensagem",
    "TipoMensagem",
    "RegraAutomacao",
    "TipoCondicao",
    "OperadorCondicao",
    "TipoAcao",
    "Condicao",
    "Acao",
    "Analytics",
    "DailyStats",
    "MetricType",
    "PeriodType",
]
