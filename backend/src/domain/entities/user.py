"""
Entidade Usuário.

Esta é a entidade principal do domínio que representa um usuário da plataforma.
Seguindo DDD, esta entidade contém apenas lógica de negócio e regras do domínio.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4


class TipoPlano(str, Enum):
    """Tipos de plano disponíveis."""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"


class StatusUsuario(str, Enum):
    """Status possíveis do usuário."""

    ATIVO = "active"
    SUSPENSO = "suspended"
    DELETADO = "deleted"


@dataclass
class ConfiguracaoPlano:
    """Configurações do plano do usuário."""

    tipo: TipoPlano = TipoPlano.FREE
    max_bots: int = 1
    max_mensagens_por_mes: int = 100
    max_contatos: int = 50
    features: List[str] = field(default_factory=list)
    expira_em: Optional[datetime] = None
    trial_termina_em: Optional[datetime] = None
    trial_utilizado: bool = False

    # Limites para features
    max_automation_rules: int = 5
    max_conversations: int = 50

    def upgrade_para(self, novo_tipo: TipoPlano, expira_em: Optional[datetime] = None) -> None:
        """Atualiza o plano do usuário."""
        self.tipo = novo_tipo
        self.expira_em = expira_em
        self._aplicar_limites()

    def _aplicar_limites(self) -> None:
        """Aplica os limites baseados no plano atual."""
        limites = {
            TipoPlano.FREE: {
                "max_bots": 1,
                "max_mensagens_por_mes": 100,
                "max_contatos": 50,
                "max_automation_rules": 5,
                "max_conversations": 50,
                "features": ["basic_automation"],
            },
            TipoPlano.BASIC: {
                "max_bots": 3,
                "max_mensagens_por_mes": 5000,
                "max_contatos": 500,
                "max_automation_rules": 10,
                "max_conversations": 100,
                "features": ["basic_automation", "llm", "analytics"],
            },
            TipoPlano.PRO: {
                "max_bots": 10,
                "max_mensagens_por_mes": 50000,
                "max_contatos": 5000,
                "max_automation_rules": 50,
                "max_conversations": 1000,
                "features": ["basic_automation", "llm", "analytics", "api_access", "priority_support"],
            },
        }

        if self.tipo in limites:
            config = limites[self.tipo]
            self.max_bots = config["max_bots"]
            self.max_mensagens_por_mes = config["max_mensagens_por_mes"]
            self.max_contatos = config["max_contatos"]
            self.max_automation_rules = config["max_automation_rules"]
            self.max_conversations = config["max_conversations"]
            self.features = config["features"]

    def tem_feature(self, feature: str) -> bool:
        """Verifica se o plano tem uma feature específica."""
        return feature in self.features

    def is_trial(self) -> bool:
        """Verifica se está em período de trial."""
        if self.trial_termina_em is None:
            return False
        return datetime.utcnow() < self.trial_termina_em

    def trial_expirado(self) -> bool:
        """Verifica se o trial expirou."""
        if self.trial_termina_em is None:
            return False
        return datetime.utcnow() > self.trial_termina_em


@dataclass
class Usuario:
    """
    Entidade que representa um usuário da plataforma.

    Atributos:
        id: Identificador único do usuário
        email: Email do usuário (único)
        telefone: Telefone do usuário
        email_confirmado: Indica se o email foi confirmado
        telefone_confirmado: Indica se o telefone foi confirmado
        senha_hash: Hash da senha (bcrypt)
        nome: Nome do usuário
        avatar: URL do avatar (opcional)
        plano: Configurações do plano
        status: Status do usuário
        criado_em: Data de criação
        atualizado_em: Data da última atualização
        ultimo_login: Data do último login
    """

    id: UUID = field(default_factory=uuid4)
    email: str = field(default="")
    telefone: Optional[str] = None
    email_confirmado: bool = False
    telefone_confirmado: bool = False
    senha_hash: Optional[str] = None
    nome: str = ""
    avatar: Optional[str] = None
    plano: ConfiguracaoPlano = field(default_factory=ConfiguracaoPlano)
    role: str = "user"
    status: StatusUsuario = StatusUsuario.ATIVO
    criado_em: datetime = field(default_factory=datetime.utcnow)
    atualizado_em: datetime = field(default_factory=datetime.utcnow)
    ultimo_login: Optional[datetime] = None

    # ========================================
    # Regras de negócio
    # ========================================

    def confirmar_email(self) -> None:
        """Confirma o email do usuário."""
        if self.email_confirmado:
            return

        self.email_confirmado = True
        self.atualizado_em = datetime.utcnow()

    def confirmar_telefone(self) -> None:
        """Confirma o telefone do usuário."""
        if self.telefone_confirmado:
            return

        self.telefone_confirmado = True
        self.atualizado_em = datetime.utcnow()

    def pode_criar_bot(self) -> bool:
        """Verifica se o usuário pode criar um novo bot."""
        return self.plano.max_bots > 0

    def registrar_login(self) -> None:
        """Registra o login do usuário."""
        self.ultimo_login = datetime.utcnow()
        self.atualizado_em = datetime.utcnow()

    def ativar(self) -> None:
        """Ativa o usuário."""
        self.status = StatusUsuario.ATIVO
        self.atualizado_em = datetime.utcnow()

    def suspender(self) -> None:
        """Suspende o usuário."""
        self.status = StatusUsuario.SUSPENSO
        self.atualizado_em = datetime.utcnow()

    def esta_ativo(self) -> bool:
        """Verifica se o usuário está ativo."""
        return self.status == StatusUsuario.ATIVO

    def pode_acessar_sistema(self) -> bool:
        """Verifica se o usuário pode acessar o sistema."""
        if not self.esta_ativo():
            return False
        if self.plano.trial_expirado() and not self.email_confirmado:
            return False
        return True

    def iniciar_trial(self, dias_trial: int) -> None:
        """Inicia o período de trial."""
        if self.plano.trial_utilizado:
            return

        self.plano.trial_utilizado = True
        self.plano.trial_termina_em = datetime.utcnow() + timedelta(days=dias_trial)
        self.atualizado_em = datetime.utcnow()

    def __post_init__(self) -> None:
        """Validações após a inicialização."""
        # Aplica limites do plano
        self.plano._aplicar_limites()
