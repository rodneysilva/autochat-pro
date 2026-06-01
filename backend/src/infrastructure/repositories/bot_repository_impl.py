"""
Implementação do repositório de bots com MongoDB.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import UUID
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.bot_repository import BotRepository
from src.domain.entities.bot import (
    Bot, TipoBot, StatusBot,
    ConfiguracaoWorkingHours, ConfiguracaoLLM,
    ItemCatalogo, ConfiguracaoCatalogo,
    ConfiguracaoWhatsApp, ConfiguracaoTelegram,
    EstatisticasBot,
)
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


def _to_object_id(raw_id) -> ObjectId:
    """Converte qualquer formato de ID para ObjectId."""
    if isinstance(raw_id, ObjectId):
        return raw_id
    return ObjectId(str(raw_id))


class MongoBotRepository(BotRepository):
    """Implementação do repositório de bots com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._collection = database.bots
        self._database = database

    # ========================================
    # Conversões Document ↔ Entidade
    # ========================================

    def _document_to_bot(self, doc: dict) -> Optional[Bot]:
        """Converte um documento do MongoDB para a entidade Bot."""
        if not doc:
            return None

        # Working Hours
        wh_data = doc.get("working_hours", {})
        working_hours = ConfiguracaoWorkingHours(
            ativado=wh_data.get("ativado", False),
            inicio=wh_data.get("inicio", "09:00"),
            fim=wh_data.get("fim", "18:00"),
            timezone=wh_data.get("timezone", "America/Sao_Paulo"),
            mensagem_fora_horario=wh_data.get("mensagem_fora_horario", ""),
        )

        # LLM Config
        llm_data = doc.get("llm_config", {})
        llm_config = ConfiguracaoLLM(
            ativado=llm_data.get("ativado", False),
            modelo=llm_data.get("modelo", "glm-4"),
            temperatura=llm_data.get("temperatura", 0.7),
            max_tokens=llm_data.get("max_tokens", 500),
            system_prompt=llm_data.get("system_prompt", ""),
            fallback_para_llm=llm_data.get("fallback_para_llm", True),
        )

        # Catálogo
        cat_data = doc.get("catalogo", {})
        itens_doc = cat_data.get("itens", [])
        itens = [
            ItemCatalogo(
                id=item.get("id", ""),
                nome=item.get("nome", ""),
                descricao=item.get("descricao", ""),
                preco=item.get("preco", 0.0),
                categoria=item.get("categoria", ""),
                imagem_url=item.get("imagem_url"),
            )
            for item in itens_doc
        ]
        catalogo = ConfiguracaoCatalogo(
            ativado=cat_data.get("ativado", False),
            itens=itens,
        )

        # WhatsApp Config
        wa_data = doc.get("whatsapp_config", {})
        whatsapp_config = ConfiguracaoWhatsApp(
            sessao=wa_data.get("sessao"),
            numero_telefone=wa_data.get("numero_telefone"),
            qr_code=wa_data.get("qr_code"),
            profile_picture_url=wa_data.get("profile_picture_url"),
        )

        # Telegram Config
        tg_data = doc.get("telegram_config", {})
        telegram_config = ConfiguracaoTelegram(
            bot_token=tg_data.get("bot_token"),
            bot_username=tg_data.get("bot_username"),
            webhook_url=tg_data.get("webhook_url"),
        )

        # Estatísticas
        stats_data = doc.get("estatisticas", {})
        estatisticas = EstatisticasBot(
            total_mensagens=stats_data.get("total_mensagens", 0),
            total_conversas=stats_data.get("total_conversas", 0),
            tempo_resposta_medio=stats_data.get("tempo_resposta_medio", 0.0),
            ultima_reset=stats_data.get("ultima_reset"),
        )

        return Bot(
            id=str(doc["_id"]),
            usuario_id=str(doc.get("user_id", "")),
            nome=doc.get("nome", ""),
            tipo=TipoBot(doc.get("tipo", "whatsapp")),
            status=StatusBot(doc.get("status", "disconnected")),
            mensagem_boas_vindas=doc.get("mensagem_boas_vindas", "Olá!"),
            mensagem_despedida=doc.get("mensagem_despedida", "Obrigado!"),
            mensagem_resposta_padrao=doc.get("mensagem_resposta_padrao", "Não entendi."),
            working_hours=working_hours,
            llm_config=llm_config,
            catalogo=catalogo,
            whatsapp_config=whatsapp_config,
            telegram_config=telegram_config,
            estatisticas=estatisticas,
            ultimo_erro=doc.get("ultimo_erro"),
            ultimo_conectado_em=doc.get("ultimo_conectado_em"),
            criado_em=doc.get("criado_em"),
            atualizado_em=doc.get("atualizado_em"),
        )

    def _bot_to_document(self, bot: Bot) -> dict:
        """Converte a entidade Bot para documento do MongoDB."""
        doc = {
            "user_id": ObjectId(bot.usuario_id) if bot.usuario_id else None,
            "nome": bot.nome,
            "tipo": bot.tipo.value if hasattr(bot.tipo, "value") else bot.tipo,
            "status": bot.status.value if hasattr(bot.status, "value") else bot.status,
            "mensagem_boas_vindas": bot.mensagem_boas_vindas,
            "mensagem_despedida": bot.mensagem_despedida,
            "mensagem_resposta_padrao": bot.mensagem_resposta_padrao,
            "working_hours": {
                "ativado": bot.working_hours.ativado,
                "inicio": bot.working_hours.inicio,
                "fim": bot.working_hours.fim,
                "timezone": bot.working_hours.timezone,
                "mensagem_fora_horario": bot.working_hours.mensagem_fora_horario,
            },
            "llm_config": {
                "ativado": bot.llm_config.ativado,
                "modelo": bot.llm_config.modelo,
                "temperatura": bot.llm_config.temperatura,
                "max_tokens": bot.llm_config.max_tokens,
                "system_prompt": bot.llm_config.system_prompt,
                "fallback_para_llm": bot.llm_config.fallback_para_llm,
            },
            "catalogo": {
                "ativado": bot.catalogo.ativado,
                "itens": [
                    {
                        "id": item.id,
                        "nome": item.nome,
                        "descricao": item.descricao,
                        "preco": item.preco,
                        "categoria": item.categoria,
                        "imagem_url": item.imagem_url,
                    }
                    for item in bot.catalogo.itens
                ],
            },
            "whatsapp_config": {
                "sessao": bot.whatsapp_config.sessao,
                "numero_telefone": bot.whatsapp_config.numero_telefone,
                "qr_code": bot.whatsapp_config.qr_code,
                "profile_picture_url": bot.whatsapp_config.profile_picture_url,
            },
            "telegram_config": {
                "bot_token": bot.telegram_config.bot_token,
                "bot_username": bot.telegram_config.bot_username,
                "webhook_url": bot.telegram_config.webhook_url,
            },
            "estatisticas": {
                "total_mensagens": bot.estatisticas.total_mensagens,
                "total_conversas": bot.estatisticas.total_conversas,
                "tempo_resposta_medio": bot.estatisticas.tempo_resposta_medio,
                "ultima_reset": bot.estatisticas.ultima_reset,
            },
            "ultimo_erro": bot.ultimo_erro,
            "ultimo_conectado_em": bot.ultimo_conectado_em,
            "atualizado_em": datetime.now(timezone.utc),
        }

        if bot.id:
            doc["criado_em"] = bot.criado_em

        return doc

    # ========================================
    # CRUD em inglês
    # ========================================

    async def create(self, bot: Bot) -> Bot:
        """Cria um novo bot."""
        doc = self._bot_to_document(bot)
        doc["criado_em"] = datetime.now(timezone.utc)

        result = await self._collection.insert_one(doc)
        created_bot = await self.find_by_id(str(result.inserted_id))

        logger.info(f"Bot criado: {created_bot.nome if created_bot else 'unknown'}")
        return created_bot

    async def find_by_id(self, bot_id: str) -> Optional[Bot]:
        """Busca um bot por ID."""
        try:
            doc = await self._collection.find_one({"_id": _to_object_id(bot_id)})
            return self._document_to_bot(doc)
        except Exception:
            return None

    async def find_by_instance_name(self, instance_name: str) -> Optional[Bot]:
        """Busca um bot pelo nome da instância WhatsApp."""
        doc = await self._collection.find_one({"nome": instance_name})
        return self._document_to_bot(doc)

    async def find_by_user(self, user_id: str) -> List[Bot]:
        """Busca bots de um usuário."""
        docs = await self._collection.find({"user_id": _to_object_id(user_id)}).to_list(None)
        return [self._document_to_bot(doc) for doc in docs if self._document_to_bot(doc)]

    async def update(self, bot: Bot) -> Bot:
        """Atualiza um bot."""
        if not bot.id:
            raise ValueError("Bot ID é obrigatório para atualização")

        doc = self._bot_to_document(bot)

        await self._collection.update_one(
            {"_id": _to_object_id(bot.id)},
            {"$set": doc},
        )

        updated_bot = await self.find_by_id(bot.id)
        logger.info(f"Bot atualizado: {updated_bot.nome if updated_bot else 'unknown'}")
        return updated_bot

    async def delete(self, bot_id: str) -> bool:
        """Deleta um bot."""
        result = await self._collection.delete_one({"_id": _to_object_id(bot_id)})
        is_deleted = result.deleted_count > 0

        if is_deleted:
            logger.info(f"Bot deletado: {bot_id}")
        return is_deleted

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusBot] = None,
    ) -> List[Bot]:
        """Lista todos os bots com paginação."""
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status.value if hasattr(status, "value") else status

        cursor = self._collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [self._document_to_bot(doc) for doc in docs if self._document_to_bot(doc)]

    async def update_status(self, bot_id: str, status: StatusBot) -> bool:
        """Atualiza o status de um bot."""
        result = await self._collection.update_one(
            {"_id": _to_object_id(bot_id)},
            {"$set": {
                "status": status.value if hasattr(status, "value") else status,
                "atualizado_em": datetime.now(timezone.utc),
            }},
        )

        if result.modified_count > 0:
            logger.info(f"Status do bot {bot_id} atualizado para {status}")
        return result.modified_count > 0

    # ========================================
    # Métodos abstratos da interface base (PT-BR)
    # ========================================

    async def salvar(self, entidade: Bot) -> Bot:
        """Salva uma entidade (cria ou atualiza)."""
        # Se o ID parece um ObjectId (24 hex chars), é atualização.
        # Se é UUID ou vazio, é criação (MongoDB gera o ObjectId).
        bot_id_str = str(entidade.id) if entidade.id else ""
        if bot_id_str and len(bot_id_str) == 24 and bot_id_str.isalnum():
            return await self.update(entidade)
        return await self.create(entidade)

    async def buscar_por_id(self, id: UUID) -> Optional[Bot]:
        """Busca uma entidade por ID."""
        return await self.find_by_id(str(id))

    async def listar(
        self,
        limite: int = 100,
        pulo: int = 0,
        filtros: Optional[dict] = None,
    ) -> List[Bot]:
        """Lista entidades com paginação e filtros."""
        query = filtros or {}
        cursor = self._collection.find(query).skip(pulo).limit(limite)
        docs = await cursor.to_list(length=limite)
        return [self._document_to_bot(doc) for doc in docs if self._document_to_bot(doc)]

    async def deletar(self, id: UUID) -> bool:
        """Deleta uma entidade por ID."""
        return await self.delete(str(id))

    async def contar(self, filtros: Optional[dict] = None) -> int:
        """Conta o total de entidades."""
        return await self._collection.count_documents(filtros or {})

    # ========================================
    # Métodos específicos do BotRepository
    # ========================================

    async def listar_por_usuario(
        self,
        usuario_id: UUID,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Bot]:
        """Lista bots de um usuário."""
        query = {"user_id": _to_object_id(usuario_id)}
        cursor = self._collection.find(query).skip(pulo).limit(limite)
        docs = await cursor.to_list(length=limite)
        return [self._document_to_bot(doc) for doc in docs if self._document_to_bot(doc)]

    async def listar_por_tipo(
        self,
        tipo: TipoBot,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Bot]:
        """Lista bots por tipo."""
        query = {"tipo": tipo.value if hasattr(tipo, "value") else tipo}
        cursor = self._collection.find(query).skip(pulo).limit(limite)
        docs = await cursor.to_list(length=limite)
        return [self._document_to_bot(doc) for doc in docs if self._document_to_bot(doc)]

    async def listar_por_status(
        self,
        status: StatusBot,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[Bot]:
        """Lista bots por status."""
        query = {"status": status.value if hasattr(status, "value") else status}
        cursor = self._collection.find(query).skip(pulo).limit(limite)
        docs = await cursor.to_list(length=limite)
        return [self._document_to_bot(doc) for doc in docs if self._document_to_bot(doc)]

    async def buscar_ativos_por_usuario(self, usuario_id: UUID) -> List[Bot]:
        """Busca bots ativos de um usuário."""
        query = {
            "user_id": _to_object_id(usuario_id),
            "status": StatusBot.ATIVO.value,
        }
        cursor = self._collection.find(query)
        docs = await cursor.to_list(length=100)
        return [self._document_to_bot(doc) for doc in docs if self._document_to_bot(doc)]

    async def contar_por_usuario(self, usuario_id: UUID) -> int:
        """Conta bots de um usuário."""
        return await self._collection.count_documents({
            "user_id": _to_object_id(usuario_id),
        })

    async def atualizar_status(
        self,
        bot_id: UUID,
        status: StatusBot,
        erro: Optional[str] = None,
    ) -> Optional[Bot]:
        """Atualiza o status de um bot."""
        update: Dict[str, Any] = {
            "status": status.value if hasattr(status, "value") else status,
            "atualizado_em": datetime.now(timezone.utc),
        }
        if erro is not None:
            update["ultimo_erro"] = erro
        else:
            update["ultimo_erro"] = None

        if status == StatusBot.ATIVO:
            update["ultimo_conectado_em"] = datetime.now(timezone.utc)

        await self._collection.update_one(
            {"_id": _to_object_id(bot_id)},
            {"$set": update},
        )

        return await self.find_by_id(str(bot_id))

    async def buscar_por_nome_instancia(self, instance_name: str) -> Optional[Bot]:
        """Busca bot pelo nome da instância (bridge)."""
        return await self.find_by_instance_name(instance_name)
