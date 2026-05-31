"""
Interface do repositório de conversas.
"""

from abc import abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.entities.conversation import Conversa, StatusConversa
from src.domain.repositories.base import Repository


class ConversationRepository(Repository[Conversa]):
    """
    Interface do repositório de conversas.

    Define os contratos específicos para operações com conversas.
    """

    @abstractmethod
    async def listar_por_bot(
        self,
        bot_id: UUID,
        status: Optional[StatusConversa] = None,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Conversa]:
        """
        Lista conversas de um bot.

        Args:
            bot_id: ID do bot
            status: Filtro por status (opcional)
            limite: Quantidade máxima de itens
            pulo: Quantidade de itens a pular

        Returns:
            Lista de conversas
        """
        pass

    @abstractmethod
    async def buscar_por_cliente(
        self,
        bot_id: UUID,
        cliente_id: str,
    ) -> Optional[Conversa]:
        """
        Busca uma conversa ativa com um cliente.

        Args:
            bot_id: ID do bot
            cliente_id: ID do cliente

        Returns:
            Conversa encontrada ou None
        """
        pass

    @abstractmethod
    async def buscar_ou_criar(
        self,
        bot_id: UUID,
        cliente_id: str,
        cliente_nome: Optional[str] = None,
    ) -> Conversa:
        """
        Busca uma conversa existente ou cria uma nova.

        Args:
            bot_id: ID do bot
            cliente_id: ID do cliente
            cliente_nome: Nome do cliente (opcional)

        Returns:
            Conversa encontrada ou criada
        """
        pass

    @abstractmethod
    async def listar_por_atendente(
        self,
        usuario_id: UUID,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Conversa]:
        """
        Lista conversas atribuídas a um atendente.

        Args:
            usuario_id: ID do usuário atendente
            limite: Quantidade máxima de itens
            pulo: Quantidade de itens a pular

        Returns:
            Lista de conversas
        """
        pass

    @abstractmethod
    async def listar_ativas_por_bot(self, bot_id: UUID) -> List[Conversa]:
        """
        Lista todas as conversas ativas de um bot.

        Args:
            bot_id: ID do bot

        Returns:
            Lista de conversas ativas
        """
        pass

    @abstractmethod
    async def contar_por_bot(self, bot_id: UUID, status: Optional[StatusConversa] = None) -> int:
        """
        Conta conversas de um bot.

        Args:
            bot_id: ID do bot
            status: Filtro por status (opcional)

        Returns:
            Total de conversas
        """
        pass

    @abstractmethod
    async def listar_inativas_desde(
        self,
        bot_id: UUID,
        desde: datetime,
        limite: int = 100,
    ) -> List[Conversa]:
        """
        Lista conversas inativas desde uma data.

        Args:
            bot_id: ID do bot
            desde: Data de referência
            limite: Quantidade máxima de itens

        Returns:
            Lista de conversas inativas
        """
        pass

    @abstractmethod
    async def atualizar_status(
        self,
        conversa_id: UUID,
        status: StatusConversa,
    ) -> Optional[Conversa]:
        """
        Atualiza o status de uma conversa.

        Args:
            conversa_id: ID da conversa
            status: Novo status

        Returns:
            Conversa atualizada ou None
        """
        pass

    @abstractmethod
    async def atribuir_atendente(
        self,
        conversa_id: UUID,
        usuario_id: UUID,
    ) -> Optional[Conversa]:
        """
        Atribui uma conversa a um atendente.

        Args:
            conversa_id: ID da conversa
            usuario_id: ID do atendente

        Returns:
            Conversa atualizada ou None
        """
        pass

    @abstractmethod
    async def remover_atribuicao(
        self,
        conversa_id: UUID,
    ) -> Optional[Conversa]:
        """
        Remove a atribuição de uma conversa.

        Args:
            conversa_id: ID da conversa

        Returns:
            Conversa atualizada ou None
        """
        pass
