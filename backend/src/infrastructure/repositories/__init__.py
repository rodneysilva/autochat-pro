"""
Implementações de repositórios concretos.
"""

from src.infrastructure.repositories.user_repository_impl import MongoUserRepository
from src.infrastructure.repositories.bot_repository_impl import MongoBotRepository
from src.infrastructure.repositories.conversation_repository_impl import MongoConversationRepository
from src.infrastructure.repositories.message_repository_impl import MongoMessageRepository
from src.infrastructure.repositories.contact_repository_impl import MongoContactRepository

__all__ = [
    "MongoUserRepository",
    "MongoBotRepository",
    "MongoConversationRepository",
    "MongoMessageRepository",
    "MongoContactRepository",
]
