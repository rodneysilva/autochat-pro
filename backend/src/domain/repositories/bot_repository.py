"""
Interface do repositório de bots.
"""

from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.bot import Bot, StatusBot, TipoBot
from src.domain.repositories.base import Repository


class BotRepository(Repository[Bot]):
    """
    Interface do repositório de bots.

    Define os contratos específicos para operações com bots.
    """

    @abstractmethod
    async def listar_por_usuario(
        self,
        usuario_id: UUID,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Bot]:
        """
        Lista bots de um usuário.

        Args:
            usuario_id: ID do usuário
            limite: Quantidade máxima de itens
            pulo: Quantidade de itens a pular

        Returns:
            Lista de bots
        """
        pass

    @abstractmethod
    async def listar_por_tipo(
        self,
        tipo: TipoBot,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Bot]:
        """
        Lista bots por tipo.

        Args:
            tipo: Tipo de bot
            limite: Quantidade máxima de itens
            pulo: Quantidade de itens a pular

        Returns:
            Lista de bots
        """
        pass

    @abstractmethod
    async def listar_por_status(
        self,
        status: StatusBot,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Bot]:
        """
        Lista bots por status.

        Args:
            status: Status do bot
            limite: Quantidade máxima de itens
            pulo: Quantidade de itens a pular

        Returns:
            Lista de bots
        """
        pass

    @abstractmethod
    async def buscar_ativos_por_usuario(self, usuario_id: UUID) -> List[Bot]:
        """
        Busca bots ativos de um usuário.

        Args:
            usuario_id: ID do usuário

        Returns:
            Lista de bots ativos
        """
        pass

    @abstractmethod
    async def contar_por_usuario(self, usuario_id: UUID) -> int:
        """
        Conta bots de um usuário.

        Args:
            usuario_id: ID do usuário

        Returns:
            Total de bots
        """
        pass

    @abstractmethod
    async def atualizar_status(
        self,
        bot_id: UUID,
        status: StatusBot,
        erro: Optional[str] = None,
    ) -> Optional[Bot]:
        """
        Atualiza o status de um bot.

        Args:
            bot_id: ID do bot
            status: Novo status
            erro: Mensagem de erro (opcional)

        Returns:
            Bot atualizado ou None
        """
        pass
