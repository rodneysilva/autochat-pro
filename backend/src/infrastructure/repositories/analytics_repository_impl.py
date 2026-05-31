"""
Implementação do repositório de analytics com MongoDB.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.analytics_repository import AnalyticsRepository, DailyStatsRepository
from src.domain.entities.analytics import Analytics, DailyStats, MetricType, PeriodType
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class MongoAnalyticsRepository(AnalyticsRepository):
    """Implementação do repositório de analytics com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        """Inicializa o repositório."""
        self._collection = database.analytics
        self._database = database

    def _document_to_analytics(self, doc: dict) -> Optional[Analytics]:
        """Converte documento MongoDB para entidade Analytics."""
        if not doc:
            return None

        return Analytics(
            id=str(doc["_id"]),
            bot_id=str(doc["bot_id"]) if "bot_id" in doc else None,
            metric_type=MetricType(doc.get("metric_type")),
            period=PeriodType(doc.get("period")),
            value=doc.get("value", 0.0),
            timestamp=doc.get("timestamp"),
            metadata=doc.get("metadata", {}),
            created_at=doc.get("created_at"),
        )

    def _analytics_to_document(self, analytics: Analytics) -> dict:
        """Converte entidade Analytics para documento MongoDB."""
        return {
            "bot_id": ObjectId(analytics.bot_id) if analytics.bot_id else None,
            "metric_type": analytics.metric_type.value,
            "period": analytics.period.value,
            "value": analytics.value,
            "timestamp": analytics.timestamp,
            "metadata": analytics.metadata,
            "created_at": analytics.created_at or datetime.utcnow(),
        }

    async def save_metric(self, analytics: Analytics) -> Analytics:
        """Salva uma métrica."""
        doc = self._analytics_to_document(analytics)
        doc["created_at"] = datetime.utcnow()

        result = await self._collection.insert_one(doc)
        created = await self.find_by_id(str(result.inserted_id))

        logger.info(f"Métrica salva: {analytics.metric_type.value}")
        return created

    async def find_by_id(self, entity_id: str) -> Optional[Analytics]:
        """Busca analytics por ID."""
        try:
            doc = await self._collection.find_one({"_id": ObjectId(entity_id)})
            return self._document_to_analytics(doc)
        except Exception:
            return None

    async def get_metrics_by_bot(
        self,
        bot_id: str,
        metric_type: Optional[MetricType] = None,
        period: Optional[PeriodType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Analytics]:
        """Busca métricas de um bot."""
        query = {"bot_id": ObjectId(bot_id)}

        if metric_type:
            query["metric_type"] = metric_type.value
        if period:
            query["period"] = period.value
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        cursor = self._collection.find(query).sort("timestamp", -1).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [self._document_to_analytics(doc) for doc in docs if doc]

    async def get_latest_metric(
        self,
        bot_id: str,
        metric_type: MetricType,
    ) -> Optional[Analytics]:
        """Busca a métrica mais recente de um tipo."""
        doc = await self._collection.find_one({
            "bot_id": ObjectId(bot_id),
            "metric_type": metric_type.value
        }).sort("timestamp", -1)

        return self._document_to_analytics(doc)

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Analytics]:
        """Lista todos os analytics."""
        cursor = self._collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._document_to_analytics(doc) for doc in docs]

    async def create(self, entity: Analytics) -> Analytics:
        """Cria analytics (alias para save_metric)."""
        return await self.save_metric(entity)

    async def update(self, entity: Analytics) -> Analytics:
        """Atualiza analytics."""
        if not entity.id:
            raise ValueError("Analytics ID is required for update")

        doc = self._analytics_to_document(entity)

        await self._collection.update_one(
            {"_id": ObjectId(entity.id)},
            {"$set": doc}
        )

        return await self.find_by_id(entity.id)

    async def delete(self, entity_id: str) -> bool:
        """Deleta analytics."""
        result = await self._collection.delete_one({"_id": ObjectId(entity_id)})
        return result.deleted_count > 0


class MongoDailyStatsRepository(DailyStatsRepository):
    """Implementação do repositório de estatísticas diárias com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        """Inicializa o repositório."""
        self._collection = database.daily_stats
        self._database = database

    def _document_to_daily_stats(self, doc: dict) -> Optional[DailyStats]:
        """Converte documento MongoDB para entidade DailyStats."""
        if not doc:
            return None

        return DailyStats(
            id=str(doc["_id"]),
            bot_id=str(doc["bot_id"]) if "bot_id" in doc else None,
            date=doc.get("date"),
            messages_sent=doc.get("messages_sent", 0),
            messages_received=doc.get("messages_received", 0),
            conversations_started=doc.get("conversations_started", 0),
            conversations_closed=doc.get("conversations_closed", 0),
            automation_responses=doc.get("automation_responses", 0),
            llm_responses=doc.get("llm_responses", 0),
            avg_response_time=doc.get("avg_response_time", 0.0),
            active_users=doc.get("active_users", 0),
            errors=doc.get("errors", 0),
            created_at=doc.get("created_at"),
        )

    def _daily_stats_to_document(self, stats: DailyStats) -> dict:
        """Converte entidade DailyStats para documento MongoDB."""
        return {
            "bot_id": ObjectId(stats.bot_id) if stats.bot_id else None,
            "date": stats.date,
            "messages_sent": stats.messages_sent,
            "messages_received": stats.messages_received,
            "conversations_started": stats.conversations_started,
            "conversations_closed": stats.conversations_closed,
            "automation_responses": stats.automation_responses,
            "llm_responses": stats.llm_responses,
            "avg_response_time": stats.avg_response_time,
            "active_users": stats.active_users,
            "errors": stats.errors,
            "created_at": stats.created_at or datetime.utcnow(),
        }

    async def save_daily_stats(self, stats: DailyStats) -> DailyStats:
        """Salva ou atualiza estatísticas diárias."""
        # Normalizar data para meia-noite
        date_key = stats.date.replace(hour=0, minute=0, second=0, microsecond=0)

        doc = self._daily_stats_to_document(stats)
        doc["date"] = date_key

        # Upsert
        result = await self._collection.update_one(
            {
                "bot_id": ObjectId(stats.bot_id),
                "date": date_key
            },
            {"$set": doc},
            upsert=True
        )

        # Buscar o documento atualizado/inserido
        updated = await self._collection.find_one({
            "bot_id": ObjectId(stats.bot_id),
            "date": date_key
        })

        return self._document_to_daily_stats(updated)

    async def get_daily_stats(
        self,
        bot_id: str,
        date: datetime,
    ) -> Optional[DailyStats]:
        """Busca estatísticas de um dia específico."""
        date_key = date.replace(hour=0, minute=0, second=0, microsecond=0)

        doc = await self._collection.find_one({
            "bot_id": ObjectId(bot_id),
            "date": date_key
        })

        return self._document_to_daily_stats(doc)

    async def get_stats_range(
        self,
        bot_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[DailyStats]:
        """Busca estatísticas em um range de datas."""
        start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        cursor = self._collection.find({
            "bot_id": ObjectId(bot_id),
            "date": {"$gte": start, "$lte": end}
        }).sort("date", 1)

        docs = await cursor.to_list(None)
        return [self._document_to_daily_stats(doc) for doc in docs if doc]

    async def increment_metric(
        self,
        bot_id: str,
        date: datetime,
        metric_field: str,
        value: int = 1,
    ) -> DailyStats:
        """Incrementa uma métrica diária (upsert)."""
        date_key = date.replace(hour=0, minute=0, second=0, microsecond=0)

        await self._collection.update_one(
            {
                "bot_id": ObjectId(bot_id),
                "date": date_key
            },
            {
                "$inc": {metric_field: value},
                "$setOnInsert": {
                    "created_at": datetime.utcnow(),
                    "messages_sent": 0,
                    "messages_received": 0,
                    "conversations_started": 0,
                    "conversations_closed": 0,
                    "automation_responses": 0,
                    "llm_responses": 0,
                    "avg_response_time": 0.0,
                    "active_users": 0,
                    "errors": 0,
                }
            },
            upsert=True
        )

        return await self.get_daily_stats(bot_id, date)

    # Métodos da interface base
    async def find_by_id(self, stats_id: str) -> Optional[DailyStats]:
        """Busca daily stats por ID."""
        try:
            doc = await self._collection.find_one({"_id": ObjectId(stats_id)})
            return self._document_to_daily_stats(doc)
        except Exception:
            return None

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[DailyStats]:
        """Lista todas as estatísticas."""
        cursor = self._collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._document_to_daily_stats(doc) for doc in docs]

    async def create(self, entity: DailyStats) -> DailyStats:
        """Cria daily stats (alias para save_daily_stats)."""
        return await self.save_daily_stats(entity)

    async def update(self, entity: DailyStats) -> DailyStats:
        """Atualiza daily stats."""
        if not entity.id:
            raise ValueError("DailyStats ID is required for update")

        doc = self._daily_stats_to_document(entity)

        await self._collection.update_one(
            {"_id": ObjectId(entity.id)},
            {"$set": doc}
        )

        return await self.find_by_id(entity.id)

    async def delete(self, entity_id: str) -> bool:
        """Deleta daily stats."""
        result = await self._collection.delete_one({"_id": ObjectId(entity_id)})
        return result.deleted_count > 0
