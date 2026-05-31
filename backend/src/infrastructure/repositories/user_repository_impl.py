"""
Implementação do repositório de usuários com MongoDB.

Este módulo fornece a implementação concreta do repositório de usuários
utilizando MongoDB como banco de dados.
"""

from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.user_repository import UserRepository
from src.domain.entities.user import Usuario, ConfiguracaoPlano, StatusUsuario
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class MongoUserRepository(UserRepository):
    """Implementação do repositório de usuários com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Inicializa o repositório.

        Args:
            database: Instância do banco de dados MongoDB.
        """
        self._collection = database.users
        self._database = database

    def _document_to_user(self, doc: dict) -> Optional[Usuario]:
        """Converte um documento do MongoDB para a entidade Usuario."""
        if not doc:
            return None

        plan_data = doc.get("plan", {})
        plan = ConfiguracaoPlano(
            tipo=plan_data.get("type", "free"),
            max_bots=plan_data.get("max_bots", 1),
            max_mensagens_por_mes=plan_data.get("max_messages_per_month", 100),
            max_contatos=plan_data.get("max_contacts", 50),
            max_automation_rules=plan_data.get("max_automation_rules", 5),
            max_conversations=plan_data.get("max_conversations", 50),
            features=plan_data.get("features", []),
            expira_em=plan_data.get("expires_at"),
            trial_termina_em=plan_data.get("trial_ends_at"),
            trial_utilizado=plan_data.get("trial_used", False),
        )

        return Usuario(
            id=str(doc["_id"]),
            email=doc.get("email", ""),
            telefone=doc.get("phone"),
            email_confirmado=doc.get("email_confirmed", False),
            telefone_confirmado=doc.get("phone_confirmed", False),
            senha_hash=doc.get("password_hash"),
            nome=doc.get("name", ""),
            avatar=doc.get("avatar"),
            plano=plan,
            status=doc.get("status", StatusUsuario.ATIVO),
            criado_em=doc.get("created_at"),
            atualizado_em=doc.get("updated_at"),
            ultimo_login=doc.get("last_login"),
        )

    def _user_to_document(self, user: Usuario) -> dict:
        """Converte a entidade Usuario para documento do MongoDB."""
        doc = {
            "email": user.email,
            "phone": user.telefone,
            "email_confirmed": user.email_confirmado,
            "phone_confirmed": user.telefone_confirmado,
            "password_hash": user.senha_hash,
            "name": user.nome,
            "avatar": user.avatar,
            "status": user.status.value if hasattr(user.status, 'value') else user.status,
            "plan": {
                "type": user.plano.tipo.value if hasattr(user.plano.tipo, 'value') else user.plano.tipo,
                "max_bots": user.plano.max_bots,
                "max_messages_per_month": user.plano.max_mensagens_por_mes,
                "max_contacts": user.plano.max_contatos,
                "max_automation_rules": user.plano.max_automation_rules,
                "max_conversations": user.plano.max_conversations,
                "features": user.plano.features,
                "expires_at": user.plano.expira_em,
                "trial_ends_at": user.plano.trial_termina_em,
                "trial_used": user.plano.trial_utilizado,
            },
            "updated_at": datetime.now(timezone.utc),
        }

        # Se já tem ID, é uma atualização
        if user.id:
            doc["created_at"] = user.criado_em

        return doc

    async def create(self, user: Usuario) -> Usuario:
        """
        Cria um novo usuário.

        Args:
            user: Entidade do usuário a ser criada.

        Returns:
            Usuário criado com ID preenchido.
        """
        doc = self._user_to_document(user)
        doc["created_at"] = datetime.now(timezone.utc)
        doc["status"] = StatusUsuario.ATIVO.value if hasattr(StatusUsuario.ATIVO, 'value') else StatusUsuario.ATIVO

        result = await self._collection.insert_one(doc)

        created_user = await self.find_by_id(str(result.inserted_id))
        logger.info(f"Usuário criado: {created_user.email if created_user else 'unknown'}")
        return created_user

    async def find_by_id(self, user_id: str) -> Optional[Usuario]:
        """
        Busca um usuário por ID.

        Args:
            user_id: ID do usuário.

        Returns:
            Usuário encontrado ou None.
        """
        try:
            doc = await self._collection.find_one({"_id": ObjectId(user_id)})
            return self._document_to_user(doc)
        except Exception:
            return None

    async def find_by_email(self, email: str) -> Optional[Usuario]:
        """
        Busca um usuário por email.

        Args:
            email: Email do usuário.

        Returns:
            Usuário encontrado ou None.
        """
        doc = await self._collection.find_one({"email": email})
        return self._document_to_user(doc)

    async def find_by_phone(self, phone: str) -> Optional[Usuario]:
        """
        Busca um usuário por telefone.

        Args:
            phone: Telefone do usuário.

        Returns:
            Usuário encontrado ou None.
        """
        doc = await self._collection.find_one({"phone": phone})
        return self._document_to_user(doc)

    async def update(self, user: Usuario) -> Usuario:
        """
        Atualiza um usuário.

        Args:
            user: Usuário com dados atualizados.

        Returns:
            Usuário atualizado.
        """
        if not user.id:
            raise ValueError("User ID is required for update")

        doc = self._user_to_document(user)

        await self._collection.update_one(
            {"_id": ObjectId(user.id)},
            {"$set": doc}
        )

        updated_user = await self.find_by_id(user.id)
        logger.info(f"Usuário atualizado: {updated_user.email if updated_user else 'unknown'}")
        return updated_user

    async def delete(self, user_id: str) -> bool:
        """
        Deleta (soft delete) um usuário.

        Args:
            user_id: ID do usuário.

        Returns:
            True se deletado com sucesso.
        """
        # Soft delete - apenas marca como deletado
        result = await self._collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"status": StatusUsuario.DELETADO.value if hasattr(StatusUsuario.DELETADO, 'value') else StatusUsuario.DELETADO, "updated_at": datetime.now(timezone.utc)}}
        )

        is_deleted = result.modified_count > 0
        if is_deleted:
            logger.info(f"Usuário deletado (soft): {user_id}")
        return is_deleted

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusUsuario] = None
    ) -> List[Usuario]:
        """
        Lista todos os usuários com paginação.

        Args:
            skip: Quantidade de registros para pular.
            limit: Quantidade máxima de registros.
            status: Filtrar por status (opcional).

        Returns:
            Lista de usuários.
        """
        query = {}
        if status:
            query["status"] = status.value if hasattr(status, 'value') else status

        cursor = self._collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [self._document_to_user(doc) for doc in docs if self._document_to_user(doc)]

    async def email_exists(self, email: str) -> bool:
        """
        Verifica se um email já está cadastrado.

        Args:
            email: Email a verificar.

        Returns:
            True se o email existe.
        """
        count = await self._collection.count_documents({"email": email})
        return count > 0

    async def phone_exists(self, phone: str) -> bool:
        """
        Verifica se um telefone já está cadastrado.

        Args:
            phone: Telefone a verificar.

        Returns:
            True se o telefone existe.
        """
        count = await self._collection.count_documents({"phone": phone})
        return count > 0

    async def set_email_confirmed(self, user_id: str) -> bool:
        """
        Marca o email do usuário como confirmado.

        Args:
            user_id: ID do usuário.

        Returns:
            True se atualizado com sucesso.
        """
        result = await self._collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "email_confirmed": True,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.modified_count > 0:
            logger.info(f"Email confirmado para usuário: {user_id}")
        return result.modified_count > 0

    async def set_phone_confirmed(self, user_id: str) -> bool:
        """
        Marca o telefone do usuário como confirmado.

        Args:
            user_id: ID do usuário.

        Returns:
            True se atualizado com sucesso.
        """
        result = await self._collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "phone_confirmed": True,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.modified_count > 0:
            logger.info(f"Telefone confirmado para usuário: {user_id}")
        return result.modified_count > 0

    async def update_password(self, user_id: str, password_hash: str) -> bool:
        """
        Atualiza a senha do usuário.

        Args:
            user_id: ID do usuário.
            password_hash: Hash da nova senha.

        Returns:
            True se atualizado com sucesso.
        """
        result = await self._collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "password_hash": password_hash,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.modified_count > 0:
            logger.info(f"Senha atualizada para usuário: {user_id}")
        return result.modified_count > 0
