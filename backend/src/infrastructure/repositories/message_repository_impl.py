"""
Implementação do repositório de mensagens com MongoDB.
"""

from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.message_repository import MessageRepository
from src.domain.entities.conversation import Mensagem, PapelMensagem, TipoMensagem
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class MongoMessageRepository(MessageRepository):
    """Implementação do repositório de mensagens com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        """Inicializa o repositório."""
        self._collection = database.messages
        self._database = database

    def _document_to_message(self, doc: dict) -> Optional[Mensagem]:
        """Converte documento MongoDB para entidade Mensagem."""
        if not doc:
            return None

        return Mensagem(
            id=str(doc["_id"]),
            conversa_id=str(doc.get("conversation_id", "")),
            papel=PapelMensagem(doc.get("role", "user")),
            conteudo=doc.get("content", ""),
            tipo=TipoMensagem(doc.get("media_type", "text")) if doc.get("media_type") else TipoMensagem.TEXTO,
            media_url=doc.get("media_url"),
            criado_em=doc.get("created_at"),
        )

    def _message_to_document(self, message: Mensagem) -> dict:
        """Converte entidade Mensagem para documento MongoDB."""
        doc = {
            "conversation_id": ObjectId(message.conversa_id) if message.conversa_id else None,
            "role": message.papel.value if hasattr(message.papel, 'value') else message.papel,
            "content": message.conteudo,
            "media_type": message.tipo.value if hasattr(message.tipo, 'value') else message.tipo,
            "media_url": message.media_url,
            "created_at": message.criado_em or datetime.now(timezone.utc),
        }

        if message.id:
            doc["created_at"] = message.criado_em

        return doc

    async def create(self, message: Mensagem) -> Mensagem:
        """Cria uma nova mensagem."""
        doc = self._message_to_document(message)
        doc["created_at"] = datetime.now(timezone.utc)

        result = await self._collection.insert_one(doc)
        created = await self.find_by_id(str(result.inserted_id))

        logger.info(f"Mensagem criada: {created.id if created else 'unknown'}")
        return created

    async def find_by_id(self, message_id: str) -> Optional[Mensagem]:
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
    ) -> List[Mensagem]:
        """Busca mensagens de uma conversa."""
        query = {"conversation_id": ObjectId(conversation_id)}

        if before_id:
            query["_id"] = {"$lt": ObjectId(before_id)}

        cursor = self._collection.find(query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)

        # Reverter para ordem cronológica
        return [self._document_to_message(doc) for doc in reversed(docs) if self._document_to_message(doc)]

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Mensagem]:
        """Lista todas as mensagens com paginação."""
        cursor = self._collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [self._document_to_message(doc) for doc in docs if self._document_to_message(doc)]

    async def count_by_conversation(self, conversation_id: str) -> int:
        """Conta mensagens de uma conversa."""
        count = await self._collection.count_documents({
            "conversation_id": ObjectId(conversation_id)
        })
        return count
