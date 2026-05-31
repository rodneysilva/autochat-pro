"""
Configuração do MongoDB para a aplicação.

Este módulo fornece a conexão com o MongoDB e funções auxiliares
para gerenciar o ciclo de vida da conexão.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from contextlib import asynccontextmanager

from src.shared.config import settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class MongoDB:
    """Cliente MongoDB singleton."""

    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls) -> None:
        """Estabelece conexão com o MongoDB."""
        if cls._client is not None:
            return

        try:
            cls._client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
            )

            # Testar conexão
            await cls._client.admin.command('ping')

            cls._database = cls._client[settings.DATABASE_NAME]

            logger.info(f"Conectado ao MongoDB: {settings.DATABASE_NAME}")

        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {e}")
            raise

    @classmethod
    async def disconnect(cls) -> None:
        """Fecha a conexão com o MongoDB."""
        if cls._client is None:
            return

        cls._client.close()
        cls._client = None
        cls._database = None
        logger.info("Desconectado do MongoDB")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Retorna a instância do banco de dados."""
        if cls._database is None:
            raise RuntimeError("MongoDB não está conectado")
        return cls._database

    @classmethod
    async def ping(cls) -> bool:
        """Verifica se a conexão está ativa."""
        try:
            await cls._client.admin.command('ping')
            return True
        except Exception:
            return False


@asynccontextmanager
async def get_database():
    """
    Context manager para obter o banco de dados.

    Garante que a conexão seja estabelecida antes de usar.
    """
    await MongoDB.connect()
    yield MongoDB.get_database()
