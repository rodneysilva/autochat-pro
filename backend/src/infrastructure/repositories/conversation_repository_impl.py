"""
Implementação do repositório de conversas com MongoDB.
"""

from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.entities.conversation import Conversation, ConversationStatus
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class MongoConversationRepository(ConversationRepository):
    """Implementação do repositório de conversas com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        """Inicializa o repositório."""
        self._collection = database.conversations
        self._database = database

    def _document_to_conversation(self, doc: dict) -> Optional[Conversation]:
        """Converte documento MongoDB para entidade Conversation."""
        if not doc:
            return None

        customer = doc.get("customer", {})

        return Conversation(
            id=str(doc["_id"]),
            bot_id=str(doc["bot_id"]) if "bot_id" in doc else None,
            customer={
                "id": customer.get("id"),
                "name": customer.get("name"),
                "metadata": customer.get("metadata", {}),
            },
            status=ConversationStatus(doc.get("status", "active")),
            assigned_to=str(doc["assigned_to"]) if doc.get("assigned_to") else None,
            last_message_at=doc.get("last_message_at"),
            created_at=doc.get("created_at"),
        )

    def _conversation_to_document(self, conversation: Conversation) -> dict:
        """Converte entidade Conversation para documento MongoDB."""
        doc = {
            "bot_id": ObjectId(conversation.bot_id) if conversation.bot_id else None,
            "customer": conversation.customer,
            "status": conversation.status.value,
            "assigned_to": ObjectId(conversation.assigned_to) if conversation.assigned_to else None,
            "last_message_at": conversation.last_message_at,
            "updated_at": datetime.utcnow(),
        }

        if conversation.id:
            doc["created_at"] = conversation.created_at

        return doc

    async def create(self, conversation: Conversation) -> Conversation:
        """Cria uma nova conversa."""
        doc = self._conversation_to_document(conversation)
        doc["created_at"] = datetime.utcnow()

        result = await self._collection.insert_one(doc)
        created = await self.find_by_id(str(result.inserted_id))

        logger.info(f"Conversa criada: {created.id}")
        return created

    async def find_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Busca conversa por ID."""
        try:
            doc = await self._collection.find_one({"_id": ObjectId(conversation_id)})
            return self._document_to_conversation(doc)
        except Exception:
            return None

    async def find_by_bot(self, bot_id: str, limit: int = 50) -> List[Conversation]:
        """Busca conversas de um bot."""
        docs = await self._collection.find(
            {"bot_id": ObjectId(bot_id)}
        ).sort("last_message_at", -1).limit(limit).to_list(None)

        return [self._document_to_conversation(doc) for doc in docs if doc]

    async def find_by_customer(self, bot_id: str, customer_id: str) -> Optional[Conversation]:
        """Busca conversa ativa de um cliente."""
        doc = await self._collection.find_one({
            "bot_id": ObjectId(bot_id),
            "customer.id": customer_id,
            "status": {"$ne": "closed"}
        })
        return self._document_to_conversation(doc)

    async def update(self, conversation: Conversation) -> Conversation:
        """Atualiza uma conversa."""
        if not conversation.id:
            raise ValueError("Conversation ID is required for update")

        doc = self._conversation_to_document(conversation)

        await self._collection.update_one(
            {"_id": ObjectId(conversation.id)},
            {"$set": doc}
        )

        updated = await self.find_by_id(conversation.id)
        logger.info(f"Conversa {conversation.id} atualizada")
        return updated

    async def update_status(self, conversation_id: str, status: ConversationStatus) -> bool:
        """Atualiza status de uma conversa."""
        result = await self._collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"status": status.value, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ConversationStatus] = None
    ) -> List[Conversation]:
        """Lista conversas com paginação."""
        query = {}
        if status:
            query["status"] = status.value

        cursor = self._collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [self._document_to_conversation(doc) for doc in docs]
