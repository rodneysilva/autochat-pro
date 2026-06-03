"""
Entidade RegraAutomacao.

Representa uma regra de automação para respostas automáticas.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class TipoCondicao(str, Enum):
    """Tipos de condição suportados."""

    KEYWORD = "keyword"
    REGEX = "regex"
    TEMPO = "time"
    INTENT = "intent"
    HAS_MEDIA = "has_media"


class OperadorCondicao(str, Enum):
    """Operadores de condição."""

    CONTEM = "contains"
    IGUAL = "equals"
    INICIA_COM = "starts_with"
    TERMINA_COM = "ends_with"
    REGEX_MATCH = "regex_match"
    MAIOR_QUE = "greater_than"
    MENOR_QUE = "less_than"


class TipoAcao(str, Enum):
    """Tipos de ação suportados."""

    RESPONDER = "reply"
    ENCAMINHAR = "forward"
    USAR_LLM = "llm"
    ADICIONAR_TAG = "tag"
    FECHAR_CONVERSA = "close"
    ATRIBUIR_HUMANO = "assign_human"


@dataclass
class Condicao:
    """Condição para acionar a regra."""

    tipo: TipoCondicao = TipoCondicao.KEYWORD
    campo: str = "message.content"
    operador: OperadorCondicao = OperadorCondicao.CONTEM
    valor: str = ""
    negar: bool = False

    def avaliar(self, contexto: Dict[str, Any]) -> bool:
        """
        Avalia a condição contra o contexto fornecido.

        Args:
            contexto: Dicionário com dados da mensagem/conversa

        Returns:
            True se a condição for satisfeita
        """
        valor_campo = self._obter_valor_campo(contexto)
        resultado = self._comparar(valor_campo)

        return not resultado if self.negar else resultado

    def _obter_valor_campo(self, contexto: Dict[str, Any]) -> Any:
        """Obtém o valor do campo do contexto."""
        campos = self.campo.split(".")
        valor = contexto

        for campo in campos:
            if isinstance(valor, dict):
                valor = valor.get(campo)
            else:
                return None

        return valor

    def _comparar(self, valor_campo: Any) -> bool:
        """Compara o valor do campo com o valor da condição."""
        if valor_campo is None:
            return False

        if self.tipo == TipoCondicao.KEYWORD:
            if self.operador == OperadorCondicao.CONTEM:
                return self.valor.lower() in str(valor_campo).lower()
            elif self.operador == OperadorCondicao.IGUAL:
                return str(valor_campo).lower() == self.valor.lower()
            elif self.operador == OperadorCondicao.INICIA_COM:
                return str(valor_campo).lower().startswith(self.valor.lower())
            elif self.operador == OperadorCondicao.TERMINA_COM:
                return str(valor_campo).lower().endswith(self.valor.lower())

        elif self.tipo == TipoCondicao.REGEX:
            import re
            if self.operador == OperadorCondicao.REGEX_MATCH:
                try:
                    return bool(re.search(self.valor, str(valor_campo), re.IGNORECASE))
                except re.error:
                    return False

        elif self.tipo == TipoCondicao.TEMPO:
            if isinstance(valor_campo, str):
                from datetime import datetime
                try:
                    hora = datetime.strptime(valor_campo, "%H:%M").time()
                    hora_inicio = datetime.strptime(self.valor.split("-")[0], "%H:%M").time()
                    hora_fim = datetime.strptime(self.valor.split("-")[1], "%H:%M").time()
                    return hora_inicio <= hora <= hora_fim
                except (ValueError, IndexError):
                    return False

        elif self.tipo == TipoCondicao.HAS_MEDIA:
            return bool(valor_campo)

        return False


@dataclass
class Acao:
    """Ação a ser executada quando a regra é acionada."""

    tipo: TipoAcao = TipoAcao.RESPONDER
    delay: int = 0  # segundos antes de executar
    conteudo: str = ""
    parametros: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EstatisticasRegra:
    """Estatísticas de execução da regra."""

    total_execucoes: int = 0
    ultima_execucao_em: Optional[datetime] = None


@dataclass
class RegraAutomacao:
    """
    Entidade que representa uma regra de automação.

    Atributos:
        id: Identificador único da regra
        bot_id: ID do bot
        nome: Nome da regra
        descricao: Descrição da regra
        ativado: Indica se a regra está ativada
        prioridade: Prioridade da regra (1-100, maior = mais prioritária)
        condicoes: Lista de condições (OR entre condições)
        acoes: Lista de ações a executar
        cooldown: Tempo de cooldown em segundos
        max_execucoes: Máximo de execuções (null = ilimitado)
        limite_por_conversa: Limite de execuções por conversa
        estatisticas: Estatísticas de execução
        criado_em: Data de criação
        atualizado_em: Data da última atualização
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    bot_id: str = ""
    nome: str = ""
    descricao: str = ""
    ativado: bool = True
    prioridade: int = 10
    condicoes: List[Condicao] = field(default_factory=list)
    acoes: List[Acao] = field(default_factory=list)
    cooldown: int = 300  # 5 minutos padrão
    max_execucoes: Optional[int] = None
    limite_por_conversa: int = 1
    estatisticas: EstatisticasRegra = field(default_factory=EstatisticasRegra)
    criado_em: datetime = field(default_factory=datetime.utcnow)
    atualizado_em: datetime = field(default_factory=datetime.utcnow)

    # Estado em memória para cooldown por conversa
    _cooldown_por_conversa: Dict[str, datetime] = field(default_factory=dict)
    _execucoes_por_conversa: Dict[str, int] = field(default_factory=dict)

    # ========================================
    # Regras de negócio
    # ========================================

    def esta_ativado(self) -> bool:
        """Verifica se a regra está ativada."""
        return self.ativado

    def pode_executar(self, conversa_id: str) -> bool:
        """
        Verifica se a regra pode ser executada para uma conversa.

        Args:
            conversa_id: ID da conversa

        Returns:
            True se pode executar
        """
        if not self.esta_ativado():
            return False

        # Verifica max_execucoes
        if self.max_execucoes and self.estatisticas.total_execucoes >= self.max_execucoes:
            return False

        # Verifica cooldown
        if self._em_cooldown(conversa_id):
            return False

        # Verifica limite por conversa
        if self._execucoes_por_conversa.get(conversa_id, 0) >= self.limite_por_conversa:
            return False

        return True

    def avaliar_condicoes(self, contexto: Dict[str, Any]) -> bool:
        """
        Avalia todas as condições (OR lógico).

        Args:
            contexto: Dicionário com dados da mensagem/conversa

        Returns:
            True se alguma condição for satisfeita
        """
        if not self.condicoes:
            return False

        # OR entre condições
        return any(condicao.avaliar(contexto) for condicao in self.condicoes)

    def executar(self, conversa_id: str) -> None:
        """
        Registra a execução da regra.

        Args:
            conversa_id: ID da conversa
        """
        # Atualiza estatísticas
        self.estatisticas.total_execucoes += 1
        self.estatisticas.ultima_execucao_em = datetime.utcnow()

        # Registra cooldown para conversa
        self._cooldown_por_conversa[conversa_id] = datetime.utcnow() + timedelta(seconds=self.cooldown)

        # Incrementa execuções por conversa
        self._execucoes_por_conversa[conversa_id] = self._execucoes_por_conversa.get(conversa_id, 0) + 1

        self.atualizado_em = datetime.utcnow()

    def _em_cooldown(self, conversa_id: str) -> bool:
        """Verifica se está em cooldown para a conversa."""
        if conversa_id not in self._cooldown_por_conversa:
            return False

        return datetime.utcnow() < self._cooldown_por_conversa[conversa_id]

    def limpar_cooldown(self, conversa_id: str) -> None:
        """Limpa o cooldown para uma conversa."""
        self._cooldown_por_conversa.pop(conversa_id, None)

    def resetar_execucoes_conversa(self, conversa_id: str) -> None:
        """Reseta o contador de execuções por conversa."""
        self._execucoes_por_conversa.pop(conversa_id, None)

    def obter_acoes_com_delay(self) -> List[tuple[int, Acao]]:
        """
        Retorna as ações ordenadas por delay.

        Returns:
            Lista de tuplas (delay, ação)
        """
        return sorted([(acao.delay, acao) for acao in self.acoes], key=lambda x: x[0])

    def ativar(self) -> None:
        """Ativa a regra."""
        self.ativado = True
        self.atualizado_em = datetime.utcnow()

    def desativar(self) -> None:
        """Desativa a regra."""
        self.ativado = False
        self.atualizado_em = datetime.utcnow()

    def adicionar_condicao(self, condicao: Condicao) -> None:
        """Adiciona uma condição à regra."""
        self.condicoes.append(condicao)
        self.atualizado_em = datetime.utcnow()

    def remover_condicao(self, indice: int) -> None:
        """Remove uma condição da regra."""
        if 0 <= indice < len(self.condicoes):
            self.condicoes.pop(indice)
            self.atualizado_em = datetime.utcnow()

    def adicionar_acao(self, acao: Acao) -> None:
        """Adiciona uma ação à regra."""
        self.acoes.append(acao)
        self.atualizado_em = datetime.utcnow()

    def remover_acao(self, indice: int) -> None:
        """Remove uma ação da regra."""
        if 0 <= indice < len(self.acoes):
            self.acoes.pop(indice)
            self.atualizado_em = datetime.utcnow()

    def resetar_estatisticas(self) -> None:
        """Reseta as estatísticas da regra."""
        self.estatisticas = EstatisticasRegra()
        self._cooldown_por_conversa.clear()
        self._execucoes_por_conversa.clear()
        self.atualizado_em = datetime.utcnow()
