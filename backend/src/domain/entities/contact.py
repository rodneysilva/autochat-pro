"""
Entidade Contato/Lead.

Representa um contato ou lead extraído das conversas dos bots.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class OrigemContato(str, Enum):
    """Origem do contato."""

    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    MANUAL = "manual"


class StatusContato(str, Enum):
    """Status do contato."""

    ATIVO = "active"
    INATIVO = "inactive"
    BLOQUEADO = "blocked"


class TagContato(str, Enum):
    """Tags de contato."""
    CLIENTE = "cliente"
    LEAD = "lead"
    PROSPECT = "prospect"
    VIP = "vip"
    SUPORTE = "suporte"


@dataclass
class Contato:
    """
    Entidade de contato/lead.

    Atributos:
        id: Identificador único
        bot_id: ID do bot de origem
        usuario_id: ID do usuário dono do bot
        nome: Nome do contato
        telefone: Número de telefone
        email: Email (opcional)
        origem: Canal de origem
        tags: Lista de tags
        status: Status do contato
        ultima_mensagem_em: Data da última mensagem
        total_mensagens: Total de mensagens trocadas
        total_conversas: Total de conversas
        metadata: Metadados adicionais
        criado_em: Data de criação
        atualizado_em: Data da última atualização
    """

    id: UUID = field(default_factory=uuid4)
    bot_id: str = ""
    usuario_id: str = ""
    nome: str = ""
    telefone: str = ""
    email: Optional[str] = None
    origem: OrigemContato = OrigemContato.WHATSAPP
    tags: List[str] = field(default_factory=list)
    status: StatusContato = StatusContato.ATIVO
    ultima_mensagem_em: Optional[datetime] = None
    total_mensagens: int = 0
    total_conversas: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    criado_em: datetime = field(default_factory=datetime.utcnow)
    atualizado_em: datetime = field(default_factory=datetime.utcnow)

    def esta_ativo(self) -> bool:
        return self.status == StatusContato.ATIVO

    def adicionar_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
            self.atualizado_em = datetime.utcnow()

    def remover_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)
            self.atualizado_em = datetime.utcnow()

    def bloquear(self) -> None:
        self.status = StatusContato.BLOQUEADO
        self.atualizado_em = datetime.utcnow()

    def desbloquear(self) -> None:
        self.status = StatusContato.ATIVO
        self.atualizado_em = datetime.utcnow()
