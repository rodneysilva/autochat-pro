"""
Implementação do repositório de bots com MongoDB.
"""

from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.bot_repository import BotRepository
from src.domain.entities.bot import Bot, BotStatus, BotType
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

        from src.domain.entities.user import Plan

        config = doc.get("config", {})
        stats = doc.get("stats", {})

        return Bot(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]) if "user_id" in doc else None,
            name=doc.get("name"),
            type=BotType(doc.get("type", "whatsapp")),
            status=BotStatus(doc.get("status", "disconnected")),
            config={
                "token": config.get("token"),
                "welcome_message": config.get("welcome_message"),
                "auto_reply_enabled": config.get("auto_reply_enabled", False),
                "llm_enabled": config.get("llm_enabled", False),
                "llm_prompt": config.get("llm_prompt"),
            },
            stats={
                "total_messages": stats.get("total_messages", 0),
                "total_conversations": stats.get("total_conversations", 0),
            },
            created_at=doc.get("created_at"),
        )

    def _bot_to_document(self, bot: Bot) -> dict:
        """Converte a entidade Bot para documento do MongoDB."""
        doc = {
            "user_id": ObjectId(bot.user_id) if bot.user_id else None,
            "name": bot.name,
            "type": bot.type.value,
            "status": bot.status.value,
            "config": {
                "token": bot.config.get("token"),
                "welcome_message": bot.config.get("welcome_message"),
                "auto_reply_enabled": bot.config.get("auto_reply_enabled", False),
                "llm_enabled": bot.config.get("llm_enabled", False),
                "llm_prompt": bot.config.get("llm_prompt"),
            },
            "stats": {
                "total_messages": bot.stats.get("total_messages", 0),
                "total_conversations": bot.stats.get("total_conversations", 0),
            },
            "updated_at": datetime.utcnow(),
        }

        # Se já tem ID, é uma atualização
        if bot.id:
            doc["created_at"] = bot.created_at

        return doc

    async def create(self, bot: Bot) -> Bot:
        """Cria um novo bot."""
        doc = self._bot_to_document(bot)
        doc["created_at"] = datetime.utcnow()

        result = await self._collection.insert_one(doc)
        created_bot = await self.find_by_id(str(result.inserted_id))

        logger.info(f"Bot criado: {created_bot.name}")
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
        return [self._document_to_bot(doc) for doc in docs if doc]

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
        logger.info(f"Bot atualizado: {updated_bot.name}")
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
        status: Optional[BotStatus] = None
    ) -> List[Bot]:
        """Lista todos os bots com paginação."""
        query = {}
        if status:
            query["status"] = status.value

        cursor = self._collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [self._document_to_bot(doc) for doc in docs]

    async def update_status(self, bot_id: str, status: BotStatus) -> bool:
        """Atualiza o status de um bot."""
        result = await self._collection.update_one(
            {"_id": ObjectId(bot_id)},
            {"$set": {"status": status.value, "updated_at": datetime.utcnow()}}
        )

        if result.modified_count > 0:
            logger.info(f"Status do bot {bot_id} atualizado para {status.value}")
        return result.modified_count > 0
