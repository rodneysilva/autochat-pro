"""
Entidade Bot.

Representa um bot de atendimento (WhatsApp ou Telegram) configurado por um usuário.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class TipoBot(str, Enum):
    """Tipos de bot suportados."""

    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class StatusBot(str, Enum):
    """Status possíveis do bot."""

    ATIVO = "active"
    PAUSADO = "paused"
    DESCONECTADO = "disconnected"
    ERRO = "error"
    CONECTANDO = "connecting"


@dataclass
class ConfiguracaoWorkingHours:
    """Configuração de horário de funcionamento."""

    ativado: bool = False
    inicio: str = "09:00"
    fim: str = "18:00"
    timezone: str = "America/Sao_Paulo"
    mensagem_fora_horario: str = "Estamos fora do horário. Retornarei em breve."


@dataclass
class ConfiguracaoLLM:
    """Configuração do LLM para o bot."""

    ativado: bool = False
    provider: str = "glm"  # glm, openai, anthropic, ollama
    modelo: str = "glm-4.7-flash"
    temperatura: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = "Você é um assistente de atendimento útil e cordial."
    fallback_para_llm: bool = True
    max_context_messages: int = 20  # Max mensagens de contexto para o LLM


@dataclass
class ItemCatalogo:
    """Item do catálogo de produtos."""

    id: str = ""
    nome: str = ""
    descricao: str = ""
    preco: float = 0.0
    categoria: str = ""
    imagem_url: Optional[str] = None


@dataclass
class ConfiguracaoCatalogo:
    """Configuração do catálogo de produtos."""

    ativado: bool = False
    itens: List[ItemCatalogo] = field(default_factory=list)


@dataclass
class ConfiguracaoWhatsApp:
    """Configurações específicas do WhatsApp."""

    sessao: Optional[str] = None
    numero_telefone: Optional[str] = None
    qr_code: Optional[str] = None
    profile_picture_url: Optional[str] = None


@dataclass
class ConfiguracaoTelegram:
    """Configurações específicas do Telegram."""

    bot_token: Optional[str] = None
    bot_username: Optional[str] = None
    webhook_url: Optional[str] = None


@dataclass
class EstatisticasBot:
    """Estatísticas do bot (cache)."""

    total_mensagens: int = 0
    total_conversas: int = 0
    tempo_resposta_medio: float = 0.0
    ultima_reset: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Bot:
    """
    Entidade que representa um bot de atendimento.

    Atributos:
        id: Identificador único do bot
        usuario_id: ID do usuário proprietário
        nome: Nome do bot
        tipo: Tipo do bot (WhatsApp ou Telegram)
        status: Status atual do bot
        mensagem_boas_vindas: Mensagem de boas-vindas
        mensagem_despedida: Mensagem de despedida
        mensagem_resposta_padrao: Resposta padrão quando não entender
        working_hours: Configuração de horário de funcionamento
        llm_config: Configuração do LLM
        catalogo: Configuração do catálogo
        whatsapp_config: Configurações específicas do WhatsApp
        telegram_config: Configurações específicas do Telegram
        estatisticas: Estatísticas do bot
        ultimo_erro: Último erro ocorrido
        ultimo_conectado_em: Timestamp da última conexão
        criado_em: Data de criação
        atualizado_em: Data da última atualização
    """

    id: UUID = field(default_factory=uuid4)
    usuario_id: UUID = field(default_factory=uuid4)
    nome: str = ""
    tipo: TipoBot = TipoBot.WHATSAPP
    status: StatusBot = StatusBot.DESCONECTADO
    mensagem_boas_vindas: str = "Olá! Sou seu assistente virtual. Como posso ajudar?"
    mensagem_despedida: str = "Obrigado pelo contato!"
    mensagem_resposta_padrao: str = "Desculpe, não entendi. Pode reformular?"
    working_hours: ConfiguracaoWorkingHours = field(default_factory=ConfiguracaoWorkingHours)
    llm_config: ConfiguracaoLLM = field(default_factory=ConfiguracaoLLM)
    catalogo: ConfiguracaoCatalogo = field(default_factory=ConfiguracaoCatalogo)
    whatsapp_config: ConfiguracaoWhatsApp = field(default_factory=ConfiguracaoWhatsApp)
    telegram_config: ConfiguracaoTelegram = field(default_factory=ConfiguracaoTelegram)
    estatisticas: EstatisticasBot = field(default_factory=EstatisticasBot)
    ultimo_erro: Optional[str] = None
    ultimo_conectado_em: Optional[datetime] = None
    criado_em: datetime = field(default_factory=datetime.utcnow)
    atualizado_em: datetime = field(default_factory=datetime.utcnow)

    # ========================================
    # Regras de negócio
    # ========================================

    def esta_conectado(self) -> bool:
        """Verifica se o bot está conectado."""
        return self.status == StatusBot.ATIVO

    def esta_ativo(self) -> bool:
        """Verifica se o bot está ativo (não pausado)."""
        return self.status in [StatusBot.ATIVO, StatusBot.CONECTANDO]

    def pode_enviar_mensagens(self) -> bool:
        """Verifica se o bot pode enviar mensagens."""
        return self.esta_conectado() and self.esta_ativo()

    def pausar(self) -> None:
        """Pausa o bot."""
        self.status = StatusBot.PAUSADO
        self.atualizado_em = datetime.utcnow()

    def retomar(self) -> None:
        """Retoma o bot."""
        if self.status == StatusBot.PAUSADO:
            self.status = StatusBot.ATIVO
            self.atualizado_em = datetime.utcnow()

    def desconectar(self, motivo: Optional[str] = None) -> None:
        """Desconecta o bot."""
        self.status = StatusBot.DESCONECTADO
        self.ultimo_conectado_em = None
        self.ultimo_erro = motivo
        self.atualizado_em = datetime.utcnow()

    def conectar(self) -> None:
        """Inicia o processo de conexão."""
        self.status = StatusBot.CONECTANDO
        self.ultimo_erro = None
        self.atualizado_em = datetime.utcnow()

    def marcar_como_conectado(self) -> None:
        """Marca o bot como conectado."""
        self.status = StatusBot.ATIVO
        self.ultimo_conectado_em = datetime.utcnow()
        self.ultimo_erro = None
        self.atualizado_em = datetime.utcnow()

    def registrar_erro(self, erro: str) -> None:
        """Registra um erro no bot."""
        self.ultimo_erro = erro
        self.status = StatusBot.ERRO
        self.atualizado_em = datetime.utcnow()

    def usar_llm(self) -> bool:
        """Verifica se o bot usa LLM."""
        return self.llm_config.ativado

    def tem_catalogo(self) -> bool:
        """Verifica se o bot tem catálogo ativo."""
        return self.catalogo.ativado and len(self.catalogo.itens) > 0

    def adicionar_item_catalogo(self, item: ItemCatalogo) -> None:
        """Adiciona um item ao catálogo."""
        if not self.catalogo.ativado:
            self.catalogo.ativado = True
        self.catalogo.itens.append(item)
        self.atualizado_em = datetime.utcnow()

    def remover_item_catalogo(self, item_id: str) -> None:
        """Remove um item do catálogo."""
        self.catalogo.itens = [i for i in self.catalogo.itens if i.id != item_id]
        if not self.catalogo.itens:
            self.catalogo.ativado = False
        self.atualizado_em = datetime.utcnow()

    def atualizar_estatisticas(self, mensagens: int = 0, conversas: int = 0, tempo_resposta: Optional[float] = None) -> None:
        """Atualiza as estatísticas do bot."""
        self.estatisticas.total_mensagens += mensagens
        self.estatisticas.total_conversas += conversas

        if tempo_resposta is not None:
            # Atualiza média móvel
            n = self.estatisticas.total_mensagens
            atual = self.estatisticas.tempo_resposta_medio
            self.estatisticas.tempo_resposta_medio = (atual * (n - 1) + tempo_resposta) / n

        self.atualizado_em = datetime.utcnow()

    def resetar_estatisticas(self) -> None:
        """Reseta as estatísticas do bot."""
        self.estatisticas = EstatisticasBot()
        self.atualizado_em = datetime.utcnow()

    def obter_configuracao_por_tipo(self) -> Optional[ConfiguracaoWhatsApp | ConfiguracaoTelegram]:
        """Retorna a configuração específica do tipo de bot."""
        if self.tipo == TipoBot.WHATSAPP:
            return self.whatsapp_config
        elif self.tipo == TipoBot.TELEGRAM:
            return self.telegram_config
        return None

    def validar_configuracao_minima(self) -> bool:
        """Valida se o bot tem configuração mínima para funcionar."""
        if self.tipo == TipoBot.WHATSAPP:
            return bool(self.whatsapp_config.sessao or self.whatsapp_config.qr_code)
        elif self.tipo == TipoBot.TELEGRAM:
            return bool(self.telegram_config.bot_token)
        return False
