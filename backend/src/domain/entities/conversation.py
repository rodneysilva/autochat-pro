"""
Entidades Conversa e Mensagem.

Representa uma conversa com um cliente e as mensagens trocadas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class StatusConversa(str, Enum):
    """Status possíveis da conversa."""

    ATIVA = "active"
    AGUARDANDO = "waiting"
    FECHADA = "closed"
    ARQUIVADA = "archived"


class PapelMensagem(str, Enum):
    """Papel do remetente da mensagem."""

    USUARIO = "user"  # Cliente
    BOT = "bot"  # Bot automático
    HUMANO = "human"  # Humano atendendo
    SISTEMA = "system"  # Mensagem do sistema


class TipoMensagem(str, Enum):
    """Tipo de conteúdo da mensagem."""

    TEXTO = "text"
    IMAGEM = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENTO = "document"
    AGRUPAR = "sticker"
    LOCALIZACAO = "location"
    CONTATO = "contact"


class StatusEntrega(str, Enum):
    """Status de entrega da mensagem."""

    PENDENTE = "pending"
    ENVIADA = "sent"
    ENTREGUE = "delivered"
    LIDA = "read"
    FALHOU = "failed"


@dataclass
class DadosCliente:
    """Informações do cliente."""

    id: str = ""  # phone number ou telegram_id
    nome: str = ""
    telefone: Optional[str] = None
    telegram_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def obter_nome_exibicao(self) -> str:
        """Retorna o nome para exibição."""
        return self.nome or self.id


@dataclass
class ContextoConversa:
    """Contexto da conversa para LLM."""

    intent_atual: Optional[str] = None
    produto_atual: Optional[str] = None
    carrinho: List[Dict[str, Any]] = field(default_factory=list)
    ultima_acao: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def limpar(self) -> None:
        """Limpa o contexto."""
        self.intent_atual = None
        self.produto_atual = None
        self.carrinho.clear()
        self.ultima_acao = None


@dataclass
class MetadataMidia:
    """Metadados de mídia."""

    mime_type: Optional[str] = None
    tamanho: Optional[int] = None
    duracao: Optional[int] = None  # para audio/video em segundos
    legenda: Optional[str] = None


@dataclass
class Conversa:
    """
    Entidade que representa uma conversa com um cliente.

    Atributos:
        id: Identificador único da conversa
        bot_id: ID do bot
        usuario_atendente_id: ID do usuário humano atendendo (opcional)
        cliente: Dados do cliente
        status: Status da conversa
        contexto: Contexto da conversa para LLM
        primeira_mensagem_em: Timestamp da primeira mensagem
        ultima_mensagem_em: Timestamp da última mensagem
        ultima_atividade_em: Timestamp da última atividade
        fechada_em: Timestamp do fechamento
        criado_em: Data de criação
        atualizado_em: Data da última atualização
    """

    id: UUID = field(default_factory=uuid4)
    bot_id: UUID = field(default_factory=uuid4)
    usuario_atendente_id: Optional[UUID] = None
    cliente: DadosCliente = field(default_factory=DadosCliente)
    status: StatusConversa = StatusConversa.ATIVA
    contexto: ContextoConversa = field(default_factory=ContextoConversa)
    primeira_mensagem_em: Optional[datetime] = None
    ultima_mensagem_em: Optional[datetime] = None
    ultima_atividade_em: Optional[datetime] = None
    fechada_em: Optional[datetime] = None
    criado_em: datetime = field(default_factory=datetime.utcnow)
    atualizado_em: datetime = field(default_factory=datetime.utcnow)

    # ========================================
    # Regras de negócio
    # ========================================

    def esta_ativa(self) -> bool:
        """Verifica se a conversa está ativa."""
        return self.status == StatusConversa.ATIVA

    def esta_fechada(self) -> bool:
        """Verifica se a conversa está fechada."""
        return self.status == StatusConversa.FECHADA

    def esta_arquivada(self) -> bool:
        """Verifica se a conversa está arquivada."""
        return self.status == StatusConversa.ARQUIVADA

    def esta_atendida_por_humano(self) -> bool:
        """Verifica se a conversa está sendo atendida por humano."""
        return self.usuario_atendente_id is not None

    def fechar(self) -> None:
        """Fecha a conversa."""
        if self.esta_fechada():
            return

        self.status = StatusConversa.FECHADA
        self.fechada_em = datetime.utcnow()
        self.atualizado_em = datetime.utcnow()

    def reabrir(self) -> None:
        """Reabre uma conversa fechada."""
        if not self.esta_fechada():
            return

        self.status = StatusConversa.ATIVA
        self.fechada_em = None
        self.atualizado_em = datetime.utcnow()

    def arquivar(self) -> None:
        """Arquiva a conversa."""
        if self.esta_arquivada():
            return

        # Primeiro fecha se estiver ativa
        if self.esta_ativa():
            self.fechar()

        self.status = StatusConversa.ARQUIVADA
        self.atualizado_em = datetime.utcnow()

    def atribuir_a_humano(self, usuario_id: UUID) -> None:
        """Atribui a conversa a um humano."""
        self.usuario_atendente_id = usuario_id
        self.status = StatusConversa.ESPERA
        self.atualizado_em = datetime.utcnow()

    def remover_atribuicao(self) -> None:
        """Remove a atribuição de humano."""
        self.usuario_atendente_id = None
        if self.status == StatusConversa.ESPERA:
            self.status = StatusConversa.ATIVA
        self.atualizado_em = datetime.utcnow()

    def registrar_mensagem(self) -> None:
        """Registra uma nova mensagem na conversa."""
        agora = datetime.utcnow()

        if self.primeira_mensagem_em is None:
            self.primeira_mensagem_em = agora

        self.ultima_mensagem_em = agora
        self.ultima_atividade_em = agora
        self.atualizado_em = agora

    def atualizar_atividade(self) -> None:
        """Atualiza o timestamp da última atividade."""
        self.ultima_atividade_em = datetime.utcnow()
        self.atualizado_em = datetime.utcnow()

    def tempo_desde_ultima_mensagem(self) -> Optional[float]:
        """Retorna o tempo em segundos desde a última mensagem."""
        if self.ultima_mensagem_em is None:
            return None

        delta = datetime.utcnow() - self.ultima_mensagem_em
        return delta.total_seconds()

    def adicionar_ao_carrinho(self, produto_id: str, quantidade: int = 1) -> None:
        """Adiciona um produto ao carrinho no contexto."""
        # Verifica se já existe
        for item in self.contexto.carrinho:
            if item.get("produto_id") == produto_id:
                item["quantidade"] += quantidade
                return

        # Adiciona novo item
        self.contexto.carrinho.append({
            "produto_id": produto_id,
            "quantidade": quantidade,
        })
        self.atualizado_em = datetime.utcnow()

    def limpar_carrinho(self) -> None:
        """Limpa o carrinho."""
        self.contexto.carrinho.clear()
        self.atualizado_em = datetime.utcnow()

    def obter_total_carrinho(self, precos: Dict[str, float]) -> float:
        """Calcula o total do carrinho."""
        total = 0.0
        for item in self.contexto.carrinho:
            produto_id = item.get("produto_id", "")
            quantidade = item.get("quantidade", 0)
            total += precos.get(produto_id, 0) * quantidade
        return total


@dataclass
class Mensagem:
    """
    Entidade que representa uma mensagem na conversa.

    Atributos:
        id: Identificador único da mensagem
        conversa_id: ID da conversa
        papel: Papel do remetente
        conteudo: Conteúdo da mensagem
        tipo: Tipo de conteúdo
        media_url: URL da mídia (se aplicável)
        media_metadata: Metadados da mídia
        provedor: Provedor da mensagem (whatsapp ou telegram)
        provedor_mensagem_id: ID da mensagem no provedor
        status_entrega: Status de entrega
        entregue_em: Timestamp de entrega
        lida_em: Timestamp de leitura
        regra_automacao_id: ID da regra que gerou a mensagem (se aplicável)
        llm_metadata: Metadados do LLM (se gerado por LLM)
        criado_em: Data de criação
    """

    id: UUID = field(default_factory=uuid4)
    conversa_id: UUID = field(default_factory=uuid4)
    papel: PapelMensagem = PapelMensagem.USUARIO
    conteudo: str = ""
    tipo: TipoMensagem = TipoMensagem.TEXTO
    media_url: Optional[str] = None
    media_metadata: Optional[MetadataMidia] = None
    provedor: str = "whatsapp"
    provedor_mensagem_id: Optional[str] = None
    status_entrega: StatusEntrega = StatusEntrega.PENDENTE
    entregue_em: Optional[datetime] = None
    lida_em: Optional[datetime] = None
    regra_automacao_id: Optional[UUID] = None
    llm_metadata: Optional[Dict[str, Any]] = None
    criado_em: datetime = field(default_factory=datetime.utcnow)

    # ========================================
    # Regras de negócio
    # ========================================

    def eh_do_cliente(self) -> bool:
        """Verifica se a mensagem é do cliente."""
        return self.papel == PapelMensagem.USUARIO

    def eh_do_bot(self) -> bool:
        """Verifica se a mensagem é do bot."""
        return self.papel == PapelMensagem.BOT

    def eh_de_humano(self) -> bool:
        """Verifica se a mensagem é de humano."""
        return self.papel == PapelMensagem.HUMANO

    def tem_midia(self) -> bool:
        """Verifica se a mensagem tem mídia."""
        return self.media_url is not None

    def marcar_como_enviada(self) -> None:
        """Marca a mensagem como enviada."""
        self.status_entrega = StatusEntrega.ENVIADA
        self.entregue_em = datetime.utcnow()

    def marcar_como_entregue(self) -> None:
        """Marca a mensagem como entregue."""
        self.status_entrega = StatusEntrega.ENTREGUE
        self.entregue_em = datetime.utcnow()

    def marcar_como_lida(self) -> None:
        """Marca a mensagem como lida."""
        if self.status_entrega != StatusEntrega.LIDA:
            self.status_entrega = StatusEntrega.LIDA
            self.lida_em = datetime.utcnow()

    def marcar_como_falhou(self) -> None:
        """Marca a mensagem como falha."""
        self.status_entrega = StatusEntrega.FALHOU

    def foi_enviada_por_automacao(self) -> bool:
        """Verifica se a mensagem foi enviada por automação."""
        return self.regra_automacao_id is not None

    def foi_gerada_por_llm(self) -> bool:
        """Verifica se a mensagem foi gerada por LLM."""
        return self.llm_metadata is not None

    def calcular_tokens(self) -> int:
        """Estima o número de tokens da mensagem."""
        # Estimativa simples: ~4 caracteres por token
        return len(self.conteudo) // 4 if self.conteudo else 0
