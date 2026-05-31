"""
Interface do repositório de mensagens.
"""

from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.conversation import Mensagem, PapelMensagem
from src.domain.repositories.base import Repository


class MessageRepository(Repository[Mensagem]):
    """
    Interface do repositório de mensagens.

    Define os contratos específicos para operações com mensagens.
    """

    @abstractmethod
    async def listar_por_conversa(
        self,
        conversa_id: UUID,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Mensagem]:
        """
        Lista mensagens de uma conversa.

        Args:
            conversa_id: ID da conversa
            limite: Quantidade máxima de itens
            pulo: Quantidade de itens a pular

        Returns:
            Lista de mensagens ordenadas por data
        """
        pass

    @abstractmethod
    async def listar_por_papel(
        self,
        conversa_id: UUID,
        papel: PapelMensagem,
        limite: int = 100,
    ) -> List[Mensagem]:
        """
        Lista mensagens de uma conversa por papel.

        Args:
            conversa_id: ID da conversa
            papel: Papel do remetente
            limite: Quantidade máxima de itens

        Returns:
            Lista de mensagens
        """
        pass

    @abstractmethod
    async def buscar_ultima_mensagem(
        self,
        conversa_id: UUID,
    ) -> Optional[Mensagem]:
        """
        Busca a última mensagem de uma conversa.

        Args:
            conversa_id: ID da conversa

        Returns:
            Última mensagem ou None
        """
        pass

    @abstractmethod
    async def contar_por_conversa(self, conversa_id: UUID) -> int:
        """
        Conta mensagens de uma conversa.

        Args:
            conversa_id: ID da conversa

        Returns:
            Total de mensagens
        """
        pass

    @abstractmethod
    async def buscar_por_provider_id(
        self,
        provider: str,
        provider_message_id: str,
    ) -> Optional[Mensagem]:
        """
        Busca uma mensagem pelo ID do provedor.

        Args:
            provider: Provedor (whatsapp ou telegram)
            provider_message_id: ID da mensagem no provedor

        Returns:
            Mensagem encontrada ou None
        """
        pass

    @abstractmethod
    async def atualizar_status_entrega(
        self,
        mensagem_id: UUID,
        status: str,
    ) -> Optional[Mensagem]:
        """
        Atualiza o status de entrega de uma mensagem.

        Args:
            mensagem_id: ID da mensagem
            status: Novo status

        Returns:
            Mensagem atualizada ou None
        """
        pass

    @abstractmethod
    async def listar_nao_lidas(
        self,
        conversa_id: UUID,
        papel: PapelMensagem = PapelMensagem.USUARIO,
    ) -> List[Mensagem]:
        """
        Lista mensagens não lidas de uma conversa.

        Args:
            conversa_id: ID da conversa
            papel: Papel das mensagens

        Returns:
            Lista de mensagens não lidas
        """
        pass

    @abstractmethod
    async def marcar_como_lidas(
        self,
        conversa_id: UUID,
        antes_de: Optional[any] = None,
    ) -> int:
        """
        Marca mensagens como lidas.

        Args:
            conversa_id: ID da conversa
            antes_de: Marcar mensagens antes desta data

        Returns:
            Quantidade de mensagens marcadas
        """
        pass

    @abstractmethod
    async def buscar_contexto_llm(
        self,
        conversa_id: UUID,
        limite: int = 20,
    ) -> List[Mensagem]:
        """
        Busca mensagens recentes para contexto do LLM.

        Args:
            conversa_id: ID da conversa
            limite: Quantidade máxima de mensagens

        Returns:
            Lista de mensagens recentes
        """
        pass
