"""
Repositório de contatos com MongoDB.
"""

from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase
from src.domain.entities.contact import Contato, StatusContato
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


def _to_object_id(raw_id) -> ObjectId:
    if isinstance(raw_id, ObjectId):
        return raw_id
    return ObjectId(str(raw_id))


class MongoContactRepository:
    """Repositório de contatos com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._collection = database.contacts
        self._database = database

    def _document_to_contact(self, doc: dict) -> Optional[Contato]:
        if not doc:
            return None
        return Contato(
            id=str(doc["_id"]),
            bot_id=str(doc.get("bot_id", "")),
            usuario_id=str(doc.get("usuario_id", "")),
            nome=doc.get("nome", ""),
            telefone=doc.get("telefone", ""),
            email=doc.get("email"),
            origem=doc.get("origem", "whatsapp"),
            tags=doc.get("tags", []),
            status=doc.get("status", "active"),
            ultima_mensagem_em=doc.get("last_message_at"),
            total_mensagens=doc.get("total_messages", 0),
            total_conversas=doc.get("total_conversations", 0),
            metadata=doc.get("metadata", {}),
            criado_em=doc.get("created_at"),
            atualizado_em=doc.get("updated_at"),
        )

    def _contact_to_document(self, contact: Contato) -> dict:
        return {
            "bot_id": _to_object_id(contact.bot_id) if contact.bot_id else None,
            "usuario_id": _to_object_id(contact.usuario_id) if contact.usuario_id else None,
            "nome": contact.nome,
            "telefone": contact.telefone,
            "email": contact.email,
            "origem": contact.origem if hasattr(contact.origem, 'value') else contact.origem,
            "tags": contact.tags,
            "status": contact.status if hasattr(contact.status, 'value') else contact.status,
            "last_message_at": contact.ultima_mensagem_em,
            "total_messages": contact.total_mensagens,
            "total_conversations": contact.total_conversas,
            "metadata": contact.metadata,
            "updated_at": datetime.now(timezone.utc),
        }

    async def salvar(self, contato: Contato) -> Contato:
        if contato.id and len(str(contato.id)) == 24 and str(contato.id).isalnum():
            doc = self._contact_to_document(contato)
            await self._collection.update_one(
                {"_id": _to_object_id(contato.id)},
                {"$set": doc},
            )
            result = await self.buscar_por_id(contato.id)
            return result if result else contato
        else:
            return await self.criar(contato)

    async def criar(self, contato: Contato) -> Contato:
        doc = self._contact_to_document(contato)
        doc["created_at"] = datetime.now(timezone.utc)
        result = await self._collection.insert_one(doc)
        return await self.buscar_por_id(str(result.inserted_id))

    async def buscar_por_id(self, contact_id) -> Optional[Contato]:
        try:
            doc = await self._collection.find_one({"_id": _to_object_id(contact_id)})
            return self._document_to_contact(doc)
        except Exception:
            return None

    async def buscar_por_telefone(self, bot_id: str, telefone: str) -> Optional[Contato]:
        try:
            doc = await self._collection.find_one({
                "bot_id": _to_object_id(bot_id),
                "telefone": telefone,
            })
            return self._document_to_contact(doc)
        except Exception:
            return None

    async def buscar_ou_criar_por_telefone(
        self, bot_id: str, usuario_id: str, telefone: str, nome: str = ""
    ) -> Contato:
        existing = await self.buscar_por_telefone(bot_id, telefone)
        if existing:
            return existing

        contato = Contato(
            bot_id=bot_id,
            usuario_id=usuario_id,
            telefone=telefone,
            nome=nome,
        )
        return await self.criar(contato)

    async def listar_por_usuario(
        self, usuario_id: str, skip: int = 0, limit: int = 50
    ) -> List[Contato]:
        try:
            docs = await self._collection.find(
                {"usuario_id": _to_object_id(usuario_id)}
            ).sort("last_message_at", -1).skip(skip).limit(limit).to_list(None)
            return [self._document_to_contact(doc) for doc in docs if self._document_to_contact(doc)]
        except Exception:
            return []

    async def listar_por_bot(
        self, bot_id: str, skip: int = 0, limit: int = 50
    ) -> List[Contato]:
        try:
            docs = await self._collection.find(
                {"bot_id": _to_object_id(bot_id)}
            ).sort("last_message_at", -1).skip(skip).limit(limit).to_list(None)
            return [self._document_to_contact(doc) for doc in docs if self._document_to_contact(doc)]
        except Exception:
            return []

    async def listar_por_tag(
        self, usuario_id: str, tag: str, limit: int = 50
    ) -> List[Contato]:
        try:
            docs = await self._collection.find({
                "usuario_id": _to_object_id(usuario_id),
                "tags": tag,
            }).sort("last_message_at", -1).limit(limit).to_list(None)
            return [self._document_to_contact(doc) for doc in docs if self._document_to_contact(doc)]
        except Exception:
            return []

    async def buscar_por_nome(
        self, usuario_id: str, nome: str, limit: int = 20
    ) -> List[Contato]:
        try:
            docs = await self._collection.find({
                "usuario_id": _to_object_id(usuario_id),
                "nome": {"$regex": nome, "$options": "i"},
            }).limit(limit).to_list(None)
            return [self._document_to_contact(doc) for doc in docs if self._document_to_contact(doc)]
        except Exception:
            return []

    async def deletar(self, contact_id) -> bool:
        result = await self._collection.delete_one({"_id": _to_object_id(contact_id)})
        return result.deleted_count > 0

    async def contar_por_usuario(self, usuario_id: str) -> int:
        return await self._collection.count_documents({
            "usuario_id": _to_object_id(usuario_id),
            "status": "active",
        })
