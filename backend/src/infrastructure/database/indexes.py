"""
Configuração de índices MongoDB.

Define todos os índices necessários para performance e relacionamentos.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


async def create_user_indexes(database: AsyncIOMotorDatabase) -> None:
    """Cria índices da coleção users."""
    await database.users.create_index("email", unique=True, sparse=True)
    await database.users.create_index("phone", unique=True, sparse=True)
    await database.users.create_index("status")
    await database.users.create_index("plan.type")
    await database.users.create_index("created_at")
    logger.info("Índices de users criados")


async def create_bot_indexes(database: AsyncIOMotorDatabase) -> None:
    """Cria índices da coleção bots."""
    await database.bots.create_index("user_id")
    await database.bots.create_index("type")
    await database.bots.create_index("status")
    await database.bots.create_index([("user_id", 1), ("status", 1)])
    await database.bots.create_index("created_at")
    logger.info("Índices de bots criados")


async def create_conversation_indexes(database: AsyncIOMotorDatabase) -> None:
    """Cria índices da coleção conversations."""
    await database.conversations.create_index("bot_id")
    await database.conversations.create_index("customer.id")
    await database.conversations.create_index("status")
    await database.conversations.create_index("last_message_at")
    await database.conversations.create_index([("bot_id", 1), ("status", 1)])
    await database.conversations.create_index([("bot_id", 1), ("customer.id", 1)])
    await database.conversations.create_index([("bot_id", 1), ("last_message_at", -1)])
    logger.info("Índices de conversations criados")


async def create_message_indexes(database: AsyncIOMotorDatabase) -> None:
    """Cria índices da coleção messages."""
    await database.messages.create_index("conversation_id")
    await database.messages.create_index("created_at")
    await database.messages.create_index([("conversation_id", 1), ("created_at", -1)])
    await database.messages.create_index([("conversation_id", 1), ("_id", 1)])
    logger.info("Índices de messages criados")


async def create_analytics_indexes(database: AsyncIOMotorDatabase) -> None:
    """Cria índices da coleção analytics."""
    await database.analytics.create_index("bot_id")
    await database.analytics.create_index("metric_type")
    await database.analytics.create_index("period")
    await database.analytics.create_index("timestamp")
    await database.analytics.create_index([("bot_id", 1), ("metric_type", 1)])
    await database.analytics.create_index([("bot_id", 1), ("timestamp", -1)])
    await database.analytics.create_index([("bot_id", 1), ("metric_type", 1), ("timestamp", -1)])
    logger.info("Índices de analytics criados")


async def create_daily_stats_indexes(database: AsyncIOMotorDatabase) -> None:
    """Cria índices da coleção daily_stats."""
    await database.daily_stats.create_index("bot_id")
    await database.daily_stats.create_index("date")
    await database.daily_stats.create_index([("bot_id", 1), ("date", -1)])
    await database.daily_stats.create_index([("bot_id", 1), ("date", 1)])
    logger.info("Índices de daily_stats criados")


async def create_automation_rule_indexes(database: AsyncIOMotorDatabase) -> None:
    """Cria índices da coleção automation_rules."""
    await database.automation_rules.create_index("bot_id")
    await database.automation_rules.create_index("enabled")
    await database.automation_rules.create_index([("bot_id", 1), ("enabled", 1)])
    await database.automation_rules.create_index("order")
    logger.info("Índices de automation_rules criados")


async def create_contact_indexes(database: AsyncIOMotorDatabase) -> None:
    """Cria índices da coleção contacts."""
    await database.contacts.create_index("bot_id")
    await database.contacts.create_index("usuario_id")
    await database.contacts.create_index("telefone")
    await database.contacts.create_index([("bot_id", 1), ("telefone", 1)])
    await database.contacts.create_index([("usuario_id", 1), ("telefone", 1)])
    await database.contacts.create_index([("usuario_id", 1), ("nome", 1)])
    await database.contacts.create_index([("bot_id", 1), ("last_message_at", -1)])
    logger.info("Índices de contacts criados")


async def create_all_indexes(database: AsyncIOMotorDatabase) -> None:
    """
    Cria todos os índices do banco de dados.

    Args:
        database: Instância do banco de dados MongoDB.
    """
    logger.info("=== Criando índices MongoDB ===")

    await create_user_indexes(database)
    await create_bot_indexes(database)
    await create_conversation_indexes(database)
    await create_message_indexes(database)
    await create_analytics_indexes(database)
    await create_daily_stats_indexes(database)
    await create_automation_rule_indexes(database)
    await create_contact_indexes(database)

    logger.info("=== Índices criados com sucesso ===")


async def drop_all_indexes(database: AsyncIOMotorDatabase) -> None:
    """
    Remove todos os índices (exceto _id).

    Útil para recriação de índices.

    Args:
        database: Instância do banco de dados MongoDB.
    """
    collections = [
        "users",
        "bots",
        "conversations",
        "messages",
        "analytics",
        "daily_stats",
        "automation_rules",
    ]

    for collection_name in collections:
        collection = database[collection_name]
        await collection.drop_indexes(except_id=True)
        logger.info(f"Índices de {collection_name} removidos")

    logger.info("=== Índices removidos ===")
