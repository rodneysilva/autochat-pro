"""
Implementação do repositório de bots com MongoDB.
"""

from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.bot_repository import BotRepository
from src.domain.entities.bot import Bot, TipoBot, StatusBot
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class MongoBotRepository(BotRepository):
    """Implementação do repositório de bots com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Inicializa o repositório.

        Args:
            database: Instância do banco de dados MongoDB.
        """
        self._collection = database.bots
        self._database = database

    def _document_to_bot(self, doc: dict) -> Optional[Bot]:
        """Converte um documento do MongoDB para a entidade Bot."""
        if not doc:
            return None

        return Bot(
            id=str(doc["_id"]),
            usuario_id=str(doc.get("user_id", "")),
            nome=doc.get("name", ""),
            tipo=TipoBot(doc.get("type", "whatsapp")),
            status=StatusBot(doc.get("status", "disconnected")),
            mensagem_boas_vindas=doc.get("welcome_message", "Olá!"),
            mensagem_despedida=doc.get("goodbye_message", "Obrigado!"),
            mensagem_resposta_padrao=doc.get("default_message", "Não entendi."),
            criado_em=doc.get("created_at"),
            atualizado_em=doc.get("updated_at"),
        )

    def _bot_to_document(self, bot: Bot) -> dict:
        """Converte a entidade Bot para documento do MongoDB."""
        doc = {
            "user_id": ObjectId(bot.usuario_id) if bot.usuario_id else None,
            "name": bot.nome,
            "type": bot.tipo.value if hasattr(bot.tipo, 'value') else bot.tipo,
            "status": bot.status.value if hasattr(bot.status, 'value') else bot.status,
            "welcome_message": bot.mensagem_boas_vindas,
            "goodbye_message": bot.mensagem_despedida,
            "default_message": bot.mensagem_resposta_padrao,
            "updated_at": datetime.now(timezone.utc),
        }

        # Se já tem ID, é uma atualização
        if bot.id:
            doc["created_at"] = bot.criado_em

        return doc

    async def create(self, bot: Bot) -> Bot:
        """Cria um novo bot."""
        doc = self._bot_to_document(bot)
        doc["created_at"] = datetime.now(timezone.utc)

        result = await self._collection.insert_one(doc)
        created_bot = await self.find_by_id(str(result.inserted_id))

        logger.info(f"Bot criado: {created_bot.nome if created_bot else 'unknown'}")
        return created_bot

    async def find_by_id(self, bot_id: str) -> Optional[Bot]:
        """Busca um bot por ID."""
        try:
            doc = await self._collection.find_one({"_id": ObjectId(bot_id)})
            return self._document_to_bot(doc)
        except Exception:
            return None

    async def find_by_user(self, user_id: str) -> List[Bot]:
        """Busca bots de um usuário."""
        docs = await self._collection.find({"user_id": ObjectId(user_id)}).to_list(None)
        return [self._document_to_bot(doc) for doc in docs if self._document_to_bot(doc)]

    async def update(self, bot: Bot) -> Bot:
        """Atualiza um bot."""
        if not bot.id:
            raise ValueError("Bot ID is required for update")

        doc = self._bot_to_document(bot)

        await self._collection.update_one(
            {"_id": ObjectId(bot.id)},
            {"$set": doc}
        )

        updated_bot = await self.find_by_id(bot.id)
        logger.info(f"Bot atualizado: {updated_bot.nome if updated_bot else 'unknown'}")
        return updated_bot

    async def delete(self, bot_id: str) -> bool:
        """Deleta um bot."""
        result = await self._collection.delete_one({"_id": ObjectId(bot_id)})
        is_deleted = result.deleted_count > 0

        if is_deleted:
            logger.info(f"Bot deletado: {bot_id}")
        return is_deleted

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusBot] = None
    ) -> List[Bot]:
        """Lista todos os bots com paginação."""
        query = {}
        if status:
            query["status"] = status.value if hasattr(status, 'value') else status

        cursor = self._collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [self._document_to_bot(doc) for doc in docs if self._document_to_bot(doc)]

    async def update_status(self, bot_id: str, status: StatusBot) -> bool:
        """Atualiza o status de um bot."""
        result = await self._collection.update_one(
            {"_id": ObjectId(bot_id)},
            {"$set": {"status": status.value if hasattr(status, 'value') else status, "updated_at": datetime.now(timezone.utc)}}
        )

        if result.modified_count > 0:
            logger.info(f"Status do bot {bot_id} atualizado para {status}")
        return result.modified_count > 0
