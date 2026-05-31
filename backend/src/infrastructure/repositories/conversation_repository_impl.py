"""
Implementação do repositório de conversas com MongoDB.
"""

from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.entities.conversation import Conversa, StatusConversa, DadosCliente
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class MongoConversationRepository(ConversationRepository):
    """Implementação do repositório de conversas com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        """Inicializa o repositório."""
        self._collection = database.conversations
        self._database = database

    def _document_to_conversation(self, doc: dict) -> Optional[Conversa]:
        """Converte documento MongoDB para entidade Conversa."""
        if not doc:
            return None

        customer_data = doc.get("customer", {})
        customer = DadosCliente(
            id=customer_data.get("id", ""),
            nome=customer_data.get("name", ""),
            telefone=customer_data.get("phone"),
            metadata=customer_data.get("metadata", {}),
        )

        return Conversa(
            id=str(doc["_id"]),
            bot_id=str(doc.get("bot_id", "")),
            cliente=customer,
            status=StatusConversa(doc.get("status", "active")),
            usuario_atendente_id=str(doc.get("assigned_to")) if doc.get("assigned_to") else None,
            ultima_mensagem_em=doc.get("last_message_at"),
            criado_em=doc.get("created_at"),
            atualizado_em=doc.get("updated_at"),
        )

    def _conversation_to_document(self, conversation: Conversa) -> dict:
        """Converte entidade Conversa para documento MongoDB."""
        doc = {
            "bot_id": ObjectId(conversation.bot_id) if conversation.bot_id else None,
            "customer": {
                "id": conversation.cliente.id,
                "name": conversation.cliente.nome,
                "phone": conversation.cliente.telefone,
                "metadata": conversation.cliente.metadata,
            },
            "status": conversation.status.value if hasattr(conversation.status, 'value') else conversation.status,
            "assigned_to": ObjectId(conversation.usuario_atendente_id) if conversation.usuario_atendente_id else None,
            "last_message_at": conversation.ultima_mensagem_em,
            "updated_at": datetime.now(timezone.utc),
        }

        if conversation.id:
            doc["created_at"] = conversation.criado_em

        return doc

    async def create(self, conversation: Conversa) -> Conversa:
        """Cria uma nova conversa."""
        doc = self._conversation_to_document(conversation)
        doc["created_at"] = datetime.now(timezone.utc)

        result = await self._collection.insert_one(doc)
        created = await self.find_by_id(str(result.inserted_id))

        logger.info(f"Conversa criada: {created.id if created else 'unknown'}")
        return created

    async def find_by_id(self, conversation_id: str) -> Optional[Conversa]:
        """Busca conversa por ID."""
        try:
            doc = await self._collection.find_one({"_id": ObjectId(conversation_id)})
            return self._document_to_conversation(doc)
        except Exception:
            return None

    async def find_by_bot(self, bot_id: str, limit: int = 50) -> List[Conversa]:
        """Busca conversas de um bot."""
        docs = await self._collection.find(
            {"bot_id": ObjectId(bot_id)}
        ).sort("last_message_at", -1).limit(limit).to_list(None)

        return [self._document_to_conversation(doc) for doc in docs if self._document_to_conversation(doc)]

    async def find_by_customer(self, bot_id: str, customer_id: str) -> Optional[Conversa]:
        """Busca conversa ativa de um cliente."""
        doc = await self._collection.find_one({
            "bot_id": ObjectId(bot_id),
            "customer.id": customer_id,
            "status": {"$ne": "closed"}
        })
        return self._document_to_conversation(doc)

    async def update(self, conversation: Conversa) -> Conversa:
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

    async def update_status(self, conversation_id: str, status: StatusConversa) -> bool:
        """Atualiza status de uma conversa."""
        result = await self._collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"status": status.value if hasattr(status, 'value') else status, "updated_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusConversa] = None
    ) -> List[Conversa]:
        """Lista conversas com paginação."""
        query = {}
        if status:
            query["status"] = status.value if hasattr(status, 'value') else status

        cursor = self._collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [self._document_to_conversation(doc) for doc in docs if self._document_to_conversation(doc)]
