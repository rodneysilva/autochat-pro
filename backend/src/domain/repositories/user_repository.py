"""
Interface do repositório de usuários.
"""

from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.user import TipoPlano, Usuario
from src.domain.repositories.base import Repository


class UserRepository(Repository[Usuario]):
    """
    Interface do repositório de usuários.

    Define os contratos específicos para operações com usuários.
    """

    @abstractmethod
    async def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """
        Busca um usuário por email.

        Args:
            email: Email do usuário

        Returns:
            Usuário encontrado ou None
        """
        pass

    @abstractmethod
    async def buscar_por_telefone(self, telefone: str) -> Optional[Usuario]:
        """
        Busca um usuário por telefone.

        Args:
            telefone: Telefone do usuário

        Returns:
            Usuário encontrado ou None
        """
        pass

    @abstractmethod
    async def listar_por_plano(
        self,
        tipo_plano: TipoPlano,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Usuario]:
        """
        Lista usuários por tipo de plano.

        Args:
            tipo_plano: Tipo de plano para filtrar
            limite: Quantidade máxima de itens
            pulo: Quantidade de itens a pular

        Returns:
            Lista de usuários
        """
        pass

    @abstractmethod
    async def contar_ativos(self) -> int:
        """
        Conta usuários ativos.

        Returns:
            Total de usuários ativos
        """
        pass

    @abstractmethod
    async def atualizar_plano(
        self,
        usuario_id: UUID,
        tipo_plano: TipoPlano,
        expira_em: Optional[any] = None,
    ) -> Optional[Usuario]:
        """
        Atualiza o plano de um usuário.

        Args:
            usuario_id: ID do usuário
            tipo_plano: Novo tipo de plano
            expira_em: Data de expiração (opcional)

        Returns:
            Usuário atualizado ou None
        """
        pass

    @abstractmethod
    async def verificar_email_existente(
        self,
        email: str,
        excluir_id: Optional[UUID] = None,
    ) -> bool:
        """
        Verifica se um email já existe.

        Args:
            email: Email a verificar
            excluir_id: ID para excluir da verificação (para atualizações)

        Returns:
            True se email já existe
        """
        pass

    @abstractmethod
    async def verificar_telefone_existente(
        self,
        telefone: str,
        excluir_id: Optional[UUID] = None,
    ) -> bool:
        """
        Verifica se um telefone já existe.

        Args:
            telefone: Telefone a verificar
            excluir_id: ID para excluir da verificação (para atualizações)

        Returns:
            True se telefone já existe
        """
        pass
