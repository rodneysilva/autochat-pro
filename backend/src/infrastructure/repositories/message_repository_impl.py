"""
Implementação do repositório de mensagens com MongoDB.
"""

from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.message_repository import MessageRepository
from src.domain.entities.message import Message, MessageRole, MediaType
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class MongoMessageRepository(MessageRepository):
    """Implementação do repositório de mensagens com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        """Inicializa o repositório."""
        self._collection = database.messages
        self._database = database

    def _document_to_message(self, doc: dict) -> Optional[Message]:
        """Converte documento MongoDB para entidade Message."""
        if not doc:
            return None

        return Message(
            id=str(doc["_id"]),
            conversation_id=str(doc["conversation_id"]) if "conversation_id" in doc else None,
            role=MessageRole(doc.get("role", "user")),
            content=doc.get("content"),
            media_type=MediaType(doc.get("media_type", "text")) if doc.get("media_type") else MediaType.TEXT,
            media_url=doc.get("media_url"),
            metadata=doc.get("metadata", {}),
            created_at=doc.get("created_at"),
        )

    def _message_to_document(self, message: Message) -> dict:
        """Converte entidade Message para documento MongoDB."""
        doc = {
            "conversation_id": ObjectId(message.conversation_id) if message.conversation_id else None,
            "role": message.role.value,
            "content": message.content,
            "media_type": message.media_type.value if message.media_type else "text",
            "media_url": message.media_url,
            "metadata": message.metadata,
            "created_at": message.created_at or datetime.utcnow(),
        }

        if message.id:
            doc["created_at"] = message.created_at

        return doc

    async def create(self, message: Message) -> Message:
        """Cria uma nova mensagem."""
        doc = self._message_to_document(message)
        doc["created_at"] = datetime.utcnow()

        result = await self._collection.insert_one(doc)
        created = await self.find_by_id(str(result.inserted_id))

        logger.info(f"Mensagem criada: {created.id}")
        return created

    async def find_by_id(self, message_id: str) -> Optional[Message]:
        """Busca mensagem por ID."""
        try:
            doc = await self._collection.find_one({"_id": ObjectId(message_id)})
            return self._document_to_message(doc)
        except Exception:
            return None

    async def find_by_conversation(
        self,
        conversation_id: str,
        limit: int = 100,
        before_id: Optional[str] = None,
    ) -> List[Message]:
        """Busca mensagens de uma conversa."""
        query = {"conversation_id": ObjectId(conversation_id)}

        if before_id:
            query["_id"] = {"$lt": ObjectId(before_id)}

        cursor = self._collection.find(query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)

        # Reverter para ordem cronológica
        return [self._document_to_message(doc) for doc in reversed(docs) if doc]

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Message]:
        """Lista todas as mensagens com paginação."""
        cursor = self._collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [self._document_to_message(doc) for doc in docs]

    async def count_by_conversation(self, conversation_id: str) -> int:
        """Conta mensagens de uma conversa."""
        count = await self._collection.count_documents({
            "conversation_id": ObjectId(conversation_id)
        })
        return count
