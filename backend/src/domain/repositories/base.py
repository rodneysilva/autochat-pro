"""
Interfaces base de repositórios.

Define o contrato que todos os repositórios devem seguir.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

# Tipo genérico para entidades
T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """
    Interface base para repositórios.

    Define os métodos CRUD básicos que todos os repositórios devem implementar.
    Seguindo o princípio de Dependency Inversion do SOLID.
    """

    @abstractmethod
    async def salvar(self, entidade: T) -> T:
        """
        Salva uma entidade (cria ou atualiza).

        Args:
            entidade: Entidade a ser salva

        Returns:
            Entidade salva
        """
        pass

    @abstractmethod
    async def buscar_por_id(self, id: UUID) -> Optional[T]:
        """
        Busca uma entidade por ID.

        Args:
            id: ID da entidade

        Returns:
            Entidade encontrada ou None
        """
        pass

    @abstractmethod
    async def listar(
        self,
        limite: int = 100,
        pulo: int = 0,
        filtros: Optional[dict] = None,
    ) -> List[T]:
        """
        Lista entidades com paginação e filtros.

        Args:
            limite: Quantidade máxima de itens
            pulo: Quantidade de itens a pular
            filtros: Filtros opcionais

        Returns:
            Lista de entidades
        """
        pass

    @abstractmethod
    async def deletar(self, id: UUID) -> bool:
        """
        Deleta uma entidade por ID.

        Args:
            id: ID da entidade

        Returns:
            True se deletou com sucesso
        """
        pass

    @abstractmethod
    async def contar(self, filtros: Optional[dict] = None) -> int:
        """
        Conta o total de entidades.

        Args:
            filtros: Filtros opcionais

        Returns:
            Total de entidades
        """
        pass
