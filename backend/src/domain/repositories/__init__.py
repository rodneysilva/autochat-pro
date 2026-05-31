"""
Módulo de repositórios do domínio.
"""

from src.domain.repositories.base import Repository
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.bot_repository import BotRepository
from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.repositories.message_repository import MessageRepository
from src.domain.repositories.automation_rule_repository import AutomationRuleRepository

__all__ = [
    "Repository",
    "UserRepository",
    "BotRepository",
    "ConversationRepository",
    "MessageRepository",
    "AutomationRuleRepository",
]
