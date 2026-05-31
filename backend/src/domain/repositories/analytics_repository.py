"""
Interface do repositório de analytics/metrics.
"""

from abc import abstractmethod
from typing import List, Optional
from datetime import datetime

from src.domain.entities.analytics import Analytics, DailyStats, MetricType, PeriodType
from src.domain.repositories.base import Repository


class AnalyticsRepository(Repository[Analytics]):
    """
    Interface do repositório de analytics.

    Define os contratos específicos para operações com métricas.
    """

    @abstractmethod
    async def save_metric(self, analytics: Analytics) -> Analytics:
        """
        Salva uma métrica.

        Args:
            analytics: Entidade Analytics a salvar.

        Returns:
            Analytics salva com ID.
        """
        pass

    @abstractmethod
    async def get_metrics_by_bot(
        self,
        bot_id: str,
        metric_type: Optional[MetricType] = None,
        period: Optional[PeriodType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Analytics]:
        """
        Busca métricas de um bot.

        Args:
            bot_id: ID do bot.
            metric_type: Tipo da métrica (opcional).
            period: Período da métrica (opcional).
            start_date: Data inicial (opcional).
            end_date: Data final (opcional).
            limit: Limite de resultados.

        Returns:
            Lista de Analytics.
        """
        pass

    @abstractmethod
    async def get_latest_metric(
        self,
        bot_id: str,
        metric_type: MetricType,
    ) -> Optional[Analytics]:
        """
        Busca a métrica mais recente de um tipo.

        Args:
            bot_id: ID do bot.
            metric_type: Tipo da métrica.

        Returns:
            Analytics mais recente ou None.
        """
        pass


class DailyStatsRepository(Repository[DailyStats]):
    """
    Interface do repositório de estatísticas diárias.

    Define os contratos específicos para operações com DailyStats.
    """

    @abstractmethod
    async def save_daily_stats(self, stats: DailyStats) -> DailyStats:
        """
        Salva ou atualiza estatísticas diárias.

        Args:
            stats: Entidade DailyStats.

        Returns:
            DailyStats salva.
        """
        pass

    @abstractmethod
    async def get_daily_stats(
        self,
        bot_id: str,
        date: datetime,
    ) -> Optional[DailyStats]:
        """
        Busca estatísticas de um dia específico.

        Args:
            bot_id: ID do bot.
            date: Data das estatísticas.

        Returns:
            DailyStats ou None.
        """
        pass

    @abstractmethod
    async def get_stats_range(
        self,
        bot_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[DailyStats]:
        """
        Busca estatísticas em um range de datas.

        Args:
            bot_id: ID do bot.
            start_date: Data inicial.
            end_date: Data final.

        Returns:
            Lista de DailyStats.
        """
        pass

    @abstractmethod
    async def increment_metric(
        self,
        bot_id: str,
        date: datetime,
        metric_field: str,
        value: int = 1,
    ) -> DailyStats:
        """
        Incrementa uma métrica diária (upsert).

        Args:
            bot_id: ID do bot.
            date: Date das estatísticas.
            metric_field: Campo a incrementar.
            value: Valor a adicionar.

        Returns:
            DailyStats atualizada.
        """
        pass
