"""
Implementação do repositório de regras de automação com MongoDB.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repositories.automation_rule_repository import AutomationRuleRepository
from src.domain.entities.automation_rule import (
    RegraAutomacao,
    Condicao,
    Acao,
    EstatisticasRegra,
    TipoCondicao,
    OperadorCondicao,
    TipoAcao,
)
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "automation_rules"


def _to_object_id(raw_id) -> ObjectId:
    """Converte qualquer formato de ID para ObjectId."""
    if isinstance(raw_id, ObjectId):
        return raw_id
    return ObjectId(str(raw_id))


def _parse_condicao(data: dict) -> Condicao:
    """Converte dict para Condicao."""
    return Condicao(
        tipo=TipoCondicao(data["tipo"]) if "tipo" in data else TipoCondicao.KEYWORD,
        campo=data.get("campo", "message.content"),
        operador=OperadorCondicao(data["operador"]) if "operador" in data else OperadorCondicao.CONTEM,
        valor=data.get("valor", ""),
        negar=data.get("negar", False),
    )


def _parse_acao(data: dict) -> Acao:
    """Converte dict para Acao."""
    return Acao(
        tipo=TipoAcao(data["tipo"]) if "tipo" in data else TipoAcao.RESPONDER,
        delay=data.get("delay", 0),
        conteudo=data.get("conteudo", ""),
        parametros=data.get("parametros", {}),
    )


def _parse_estatisticas(data: dict) -> EstatisticasRegra:
    """Converte dict para EstatisticasRegra."""
    ultima = data.get("ultima_execucao_em")
    if isinstance(ultima, str):
        from dateutil.parser import parse as parse_dt
        ultima = parse_dt(ultima)
    return EstatisticasRegra(
        total_execucoes=data.get("total_execucoes", 0),
        ultima_execucao_em=ultima,
    )


class MongoAutomationRuleRepository(AutomationRuleRepository):
    """Implementação do repositório de regras de automação com MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._collection = database[COLLECTION_NAME]

    # ========================================
    # Conversões Document ↔ Entidade
    # ========================================

    def _document_to_entity(self, doc: dict) -> Optional[RegraAutomacao]:
        """Converte um documento do MongoDB para a entidade RegraAutomacao."""
        if not doc:
            return None

        condicoes = [_parse_condicao(c) for c in doc.get("condicoes", [])]
        acoes = [_parse_acao(a) for a in doc.get("acoes", [])]
        stats = _parse_estatisticas(doc.get("estatisticas", {}))

        return RegraAutomacao(
            id=str(doc["_id"]),
            bot_id=str(doc.get("bot_id", "")),
            nome=doc.get("nome", ""),
            descricao=doc.get("descricao", ""),
            ativado=doc.get("ativado", True),
            prioridade=doc.get("prioridade", 10),
            condicoes=condicoes,
            acoes=acoes,
            cooldown=doc.get("cooldown", 300),
            max_execucoes=doc.get("max_execucoes"),
            limite_por_conversa=doc.get("limite_por_conversa", 1),
            estatisticas=stats,
            criado_em=doc.get("criado_em"),
            atualizado_em=doc.get("atualizado_em"),
        )

    def _entity_to_document(self, rule: RegraAutomacao) -> dict:
        """Converte a entidade para documento do MongoDB."""
        stats = rule.estatisticas
        return {
            "bot_id": ObjectId(rule.bot_id) if rule.bot_id else None,
            "nome": rule.nome,
            "descricao": rule.descricao,
            "ativado": rule.ativado,
            "prioridade": rule.prioridade,
            "condicoes": [
                {
                    "tipo": c.tipo.value,
                    "campo": c.campo,
                    "operador": c.operador.value,
                    "valor": c.valor,
                    "negar": c.negar,
                }
                for c in rule.condicoes
            ],
            "acoes": [
                {
                    "tipo": a.tipo.value,
                    "delay": a.delay,
                    "conteudo": a.conteudo,
                    "parametros": a.parametros,
                }
                for a in rule.acoes
            ],
            "cooldown": rule.cooldown,
            "max_execucoes": rule.max_execucoes,
            "limite_por_conversa": rule.limite_por_conversa,
            "estatisticas": {
                "total_execucoes": stats.total_execucoes,
                "ultima_execucao_em": stats.ultima_execucao_em.isoformat() if stats.ultima_execucao_em else None,
            },
            "atualizado_em": datetime.now(timezone.utc),
        }

    # ========================================
    # Base Repository (PT-BR)
    # ========================================

    async def salvar(self, entidade: RegraAutomacao) -> RegraAutomacao:
        """Salva uma entidade (cria ou atualiza)."""
        rule_id = str(entidade.id) if entidade.id else ""
        if rule_id and len(rule_id) == 24 and rule_id.isalnum():
            return await self.atualizar(entidade)
        return await self.criar(entidade)

    async def buscar_por_id(self, id: str) -> Optional[RegraAutomacao]:
        """Busca uma entidade por ID."""
        try:
            doc = await self._collection.find_one({"_id": _to_object_id(id)})
            return self._document_to_entity(doc)
        except Exception:
            return None

    async def listar(
        self,
        limite: int = 100,
        pulo: int = 0,
        filtros: Optional[dict] = None,
    ) -> List[RegraAutomacao]:
        """Lista entidades com paginação e filtros."""
        query = filtros or {}
        cursor = self._collection.find(query).sort("prioridade", -1).skip(pulo).limit(limite)
        docs = await cursor.to_list(length=limite)
        return [self._document_to_entity(d) for d in docs if self._document_to_entity(d)]

    async def deletar(self, id: str) -> bool:
        """Deleta uma entidade por ID."""
        result = await self._collection.delete_one({"_id": _to_object_id(id)})
        return result.deleted_count > 0

    async def contar(self, filtros: Optional[dict] = None) -> int:
        """Conta o total de entidades."""
        return await self._collection.count_documents(filtros or {})

    # ========================================
    # Interface específica
    # ========================================

    async def criar(self, rule: RegraAutomacao) -> RegraAutomacao:
        """Cria uma nova regra."""
        doc = self._entity_to_document(rule)
        doc["criado_em"] = datetime.now(timezone.utc)
        result = await self._collection.insert_one(doc)
        created = await self._get_by_object_id(result.inserted_id)
        logger.info(f"Regra criada: {created.nome if created else 'unknown'}")
        return created

    async def atualizar(self, rule: RegraAutomacao) -> RegraAutomacao:
        """Atualiza uma regra existente."""
        if not rule.id:
            raise ValueError("ID obrigatório para atualização")
        doc = self._entity_to_document(rule)
        await self._collection.update_one(
            {"_id": _to_object_id(rule.id)},
            {"$set": doc},
        )
        updated = await self._get_by_object_id(_to_object_id(rule.id))
        logger.info(f"Regra atualizada: {updated.nome if updated else 'unknown'}")
        return updated

    async def _get_by_object_id(self, oid: ObjectId) -> Optional[RegraAutomacao]:
        doc = await self._collection.find_one({"_id": oid})
        return self._document_to_entity(doc)

    async def buscar_por_nome(self, bot_id: str, nome: str) -> Optional[RegraAutomacao]:
        """Busca regra por nome dentro de um bot."""
        doc = await self._collection.find_one({
            "bot_id": _to_object_id(bot_id),
            "nome": nome,
        })
        return self._document_to_entity(doc)

    async def listar_por_bot(
        self,
        bot_id: str,
        apenas_ativas: bool = False,
        limite: int = 100,
        pulo: int = 0,
    ) -> List[RegraAutomacao]:
        """Lista regras de um bot ordenadas por prioridade."""
        query: Dict[str, Any] = {"bot_id": _to_object_id(bot_id)}
        if apenas_ativas:
            query["ativado"] = True
        cursor = self._collection.find(query).sort("prioridade", -1).skip(pulo).limit(limite)
        docs = await cursor.to_list(length=limite)
        return [self._document_to_entity(d) for d in docs if self._document_to_entity(d)]

    async def buscar_ativas_por_bot(self, bot_id: str) -> List[RegraAutomacao]:
        """Busca todas as regras ativas de um bot."""
        query = {"bot_id": _to_object_id(bot_id), "ativado": True}
        cursor = self._collection.find(query).sort("prioridade", -1)
        docs = await cursor.to_list(length=1000)
        return [self._document_to_entity(d) for d in docs if self._document_to_entity(d)]

    async def contar_por_bot(self, bot_id: str, apenas_ativas: bool = False) -> int:
        """Conta regras de um bot."""
        query: Dict[str, Any] = {"bot_id": _to_object_id(bot_id)}
        if apenas_ativas:
            query["ativado"] = True
        return await self._collection.count_documents(query)

    async def atualizar_status_ativacao(
        self,
        regra_id: str,
        ativada: bool,
    ) -> Optional[RegraAutomacao]:
        """Atualiza o status de ativação de uma regra."""
        await self._collection.update_one(
            {"_id": _to_object_id(regra_id)},
            {"$set": {
                "ativado": ativada,
                "atualizado_em": datetime.now(timezone.utc),
            }},
        )
        return await self.buscar_por_id(regra_id)

    async def buscar_por_prioridade(
        self,
        bot_id: str,
        prioridade_minima: int,
        prioridade_maxima: int,
    ) -> List[RegraAutomacao]:
        """Busca regras por faixa de prioridade."""
        query = {
            "bot_id": _to_object_id(bot_id),
            "prioridade": {"$gte": prioridade_minima, "$lte": prioridade_maxima},
        }
        cursor = self._collection.find(query).sort("prioridade", -1)
        docs = await cursor.to_list(length=1000)
        return [self._document_to_entity(d) for d in docs if self._document_to_entity(d)]
