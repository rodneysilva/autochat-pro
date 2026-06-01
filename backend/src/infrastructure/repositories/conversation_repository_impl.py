"""
Implementação do repositório de conversas com MongoDB.
"""

from typing import Optional, List
from datetime import datetime, timezone
from uuid import UUID, uuid4
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.entities.conversation import Conversa, StatusConversa, DadosCliente
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


def _to_object_id(raw_id) -> ObjectId:
    """Converte qualquer formato de ID para ObjectId."""
    if isinstance(raw_id, ObjectId):
        return raw_id
    return ObjectId(str(raw_id))


class MongoConversationRepository(ConversationRepository):
    """Implementação do repositório de conversas com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
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
            primeira_mensagem_em=doc.get("first_message_at"),
            ultima_mensagem_em=doc.get("last_message_at"),
            criado_em=doc.get("created_at"),
            atualizado_em=doc.get("updated_at"),
        )

    def _conversation_to_document(self, conversation: Conversa) -> dict:
        """Converte entidade Conversa para documento MongoDB."""
        doc = {
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

        if conversation.bot_id:
            doc["bot_id"] = _to_object_id(conversation.bot_id)

        if conversation.primeira_mensagem_em:
            doc["first_message_at"] = conversation.primeira_mensagem_em

        if conversation.criado_em:
            doc["created_at"] = conversation.criado_em

        return doc

    # ========================================
    # Base Repository methods
    # ========================================

    async def salvar(self, entidade: Conversa) -> Conversa:
        """Salva (cria ou atualiza) uma conversa."""
        if entidade.id and len(str(entidade.id)) == 24 and str(entidade.id).isalnum():
            # Update
            doc = self._conversation_to_document(entidade)
            await self._collection.update_one(
                {"_id": _to_object_id(entidade.id)},
                {"$set": doc},
            )
            return await self.buscar_por_id(entidade.id)
        else:
            # Create
            return await self.create(entidade)

    async def buscar_por_id(self, id: UUID) -> Optional[Conversa]:
        """Busca conversa por ID."""
        try:
            doc = await self._collection.find_one({"_id": _to_object_id(id)})
            return self._document_to_conversation(doc)
        except Exception:
            return None

    async def listar(
        self,
        filtros: Optional[dict] = None,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Conversa]:
        """Lista conversas com filtros e paginação."""
        query = filtros or {}
        docs = await self._collection.find(query).skip(pulo).limit(limite).to_list(None)
        return [self._document_to_conversation(doc) for doc in docs if self._document_to_conversation(doc)]

    async def deletar(self, id: UUID) -> bool:
        """Deleta uma conversa."""
        result = await self._collection.delete_one({"_id": _to_object_id(id)})
        return result.deleted_count > 0

    async def contar(self, filtros: Optional[dict] = None) -> int:
        """Conta conversas."""
        query = filtros or {}
        return await self._collection.count_documents(query)

    # ========================================
    # Interface-specific methods
    # ========================================

    async def create(self, conversation: Conversa) -> Conversa:
        """Cria uma nova conversa."""
        doc = self._conversation_to_document(conversation)
        doc["created_at"] = datetime.now(timezone.utc)

        result = await self._collection.insert_one(doc)
        created = await self.find_by_id(str(result.inserted_id))
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
        try:
            docs = await self._collection.find(
                {"bot_id": _to_object_id(bot_id)}
            ).sort("last_message_at", -1).limit(limit).to_list(None)
            return [self._document_to_conversation(doc) for doc in docs if self._document_to_conversation(doc)]
        except Exception:
            return []

    async def find_by_customer(self, bot_id: str, customer_id: str) -> Optional[Conversa]:
        """Busca conversa ativa de um cliente."""
        try:
            doc = await self._collection.find_one({
                "bot_id": _to_object_id(bot_id),
                "customer.id": customer_id,
                "status": {"$ne": "closed"}
            })
            return self._document_to_conversation(doc)
        except Exception:
            return None

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

        docs = await self._collection.find(query).skip(skip).limit(limit).to_list(None)
        return [self._document_to_conversation(doc) for doc in docs if self._document_to_conversation(doc)]

    # ========================================
    # Abstract methods from ConversationRepository
    # ========================================

    async def listar_por_bot(
        self,
        bot_id: UUID,
        status: Optional[StatusConversa] = None,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Conversa]:
        """Lista conversas de um bot."""
        query: dict = {"bot_id": _to_object_id(bot_id)}
        if status:
            query["status"] = status.value if hasattr(status, 'value') else status
        docs = await self._collection.find(query).skip(pulo).limit(limite).to_list(None)
        return [self._document_to_conversation(doc) for doc in docs if self._document_to_conversation(doc)]

    async def buscar_por_cliente(
        self, bot_id: UUID, cliente_id: str,
    ) -> Optional[Conversa]:
        """Busca conversa ativa de um cliente."""
        return await self.find_by_customer(str(bot_id), cliente_id)

    async def buscar_ou_criar(
        self,
        bot_id: UUID,
        cliente_id: str,
        cliente_nome: Optional[str] = None,
    ) -> Conversa:
        """Busca conversa existente ou cria nova."""
        existing = await self.find_by_customer(str(bot_id), cliente_id)
        if existing:
            return existing

        conversa = Conversa(
            bot_id=str(bot_id),
            cliente=DadosCliente(id=cliente_id, nome=cliente_nome or ""),
            status=StatusConversa.ATIVA,
            criado_em=datetime.now(timezone.utc),
            atualizado_em=datetime.now(timezone.utc),
        )
        return await self.create(conversa)

    async def listar_por_atendente(
        self, usuario_id: UUID, limite: int = 100, pulo: int = 0,
    ) -> List[Conversa]:
        """Lista conversas de um atendente."""
        docs = await self._collection.find(
            {"assigned_to": _to_object_id(usuario_id)}
        ).skip(pulo).limit(limite).to_list(None)
        return [self._document_to_conversation(doc) for doc in docs if self._document_to_conversation(doc)]

    async def listar_ativas_por_bot(self, bot_id: UUID) -> List[Conversa]:
        """Lista conversas ativas de um bot."""
        return await self.listar_por_bot(bot_id, status=StatusConversa.ATIVA)

    async def contar_por_bot(
        self, bot_id: UUID, status: Optional[StatusConversa] = None,
    ) -> int:
        """Conta conversas de um bot."""
        query: dict = {"bot_id": _to_object_id(bot_id)}
        if status:
            query["status"] = status.value if hasattr(status, 'value') else status
        return await self._collection.count_documents(query)

    async def listar_inativas_desde(
        self, bot_id: UUID, desde: datetime, limite: int = 100,
    ) -> List[Conversa]:
        """Lista conversas inativas desde uma data."""
        docs = await self._collection.find({
            "bot_id": _to_object_id(bot_id),
            "last_message_at": {"$lt": desde},
        }).limit(limite).to_list(None)
        return [self._document_to_conversation(doc) for doc in docs if self._document_to_conversation(doc)]

    async def atualizar_status(
        self, conversa_id: UUID, status: StatusConversa,
    ) -> Optional[Conversa]:
        """Atualiza status de uma conversa."""
        await self.update_status(str(conversa_id), status)
        return await self.find_by_id(str(conversa_id))

    async def atribuir_atendente(
        self, conversa_id: UUID, usuario_id: UUID,
    ) -> Optional[Conversa]:
        """Atribui atendente a uma conversa."""
        await self._collection.update_one(
            {"_id": _to_object_id(conversa_id)},
            {"$set": {
                "assigned_to": _to_object_id(usuario_id),
                "status": "waiting",
                "updated_at": datetime.now(timezone.utc),
            }}
        )
        return await self.find_by_id(str(conversa_id))

    async def remover_atribuicao(
        self, conversa_id: UUID,
    ) -> Optional[Conversa]:
        """Remove atribuição de atendente."""
        await self._collection.update_one(
            {"_id": _to_object_id(conversa_id)},
            {"$set": {
                "assigned_to": None,
                "status": "active",
                "updated_at": datetime.now(timezone.utc),
            }}
        )
        return await self.find_by_id(str(conversa_id))
