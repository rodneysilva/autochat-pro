"""
Interface do repositório de regras de automação.
"""

from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.automation_rule import RegraAutomacao
from src.domain.repositories.base import Repository


class AutomationRuleRepository(Repository[RegraAutomacao]):
    """
    Interface do repositório de regras de automação.

    Define os contratos específicos para operações com regras.
    """

    @abstractmethod
    async def listar_por_bot(
        self,
        bot_id: UUID,
        apenas_ativas: bool = False,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[RegraAutomacao]:
        """
        Lista regras de um bot.

        Args:
            bot_id: ID do bot
            apenas_ativas: Se True, retorna apenas regras ativas
            limite: Quantidade máxima de itens
            pulo: Quantidade de itens a pular

        Returns:
            Lista de regras ordenadas por prioridade
        """
        pass

    @abstractmethod
    async def buscar_ativas_por_bot(self, bot_id: UUID) -> List[RegraAutomacao]:
        """
        Busca todas as regras ativas de um bot.

        Args:
            bot_id: ID do bot

        Returns:
            Lista de regras ativas ordenadas por prioridade
        """
        pass

    @abstractmethod
    async def contar_por_bot(self, bot_id: UUID, apenas_ativas: bool = False) -> int:
        """
        Conta regras de um bot.

        Args:
            bot_id: ID do bot
            apenas_ativas: Se True, conta apenas regras ativas

        Returns:
            Total de regras
        """
        pass

    @abstractmethod
    async def atualizar_status_ativacao(
        self,
        regra_id: UUID,
        ativada: bool,
    ) -> Optional[RegraAutomacao]:
        """
        Atualiza o status de ativação de uma regra.

        Args:
            regra_id: ID da regra
            ativada: Novo status

        Returns:
            Regra atualizada ou None
        """
        pass

    @abstractmethod
    async def buscar_por_prioridade(
        self,
        bot_id: UUID,
        prioridade_minima: int,
        prioridade_maxima: int,
    ) -> List[RegraAutomacao]:
        """
        Busca regras por faixa de prioridade.

        Args:
            bot_id: ID do bot
            prioridade_minima: Prioridade mínima
            prioridade_maxima: Prioridade máxima

        Returns:
            Lista de regras
        """
        pass
