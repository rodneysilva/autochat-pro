"""
Testes de domínio — entidades e regras de negócio.
"""

import pytest
from src.domain.entities.user import Usuario, ConfiguracaoPlano, StatusUsuario, TipoPlano
from src.domain.entities.automation_rule import (
    RegraAutomacao, Condicao, Acao,
    TipoCondicao, OperadorCondicao, TipoAcao,
)
from src.domain.entities.bot import Bot, StatusBot, TipoBot


class TestUsuario:
    """Testes da entidade Usuario."""

    def test_criar_usuario(self):
        user = Usuario(
            email="teste@teste.com",
            nome="Teste",
            senha_hash="hash123",
        )
        assert user.email == "teste@teste.com"
        assert user.role == "user"  # default
        assert user.status == StatusUsuario.ATIVO

    def test_confirmar_email(self):
        user = Usuario(email="teste@teste.com")
        assert user.email_confirmado is False
        user.confirmar_email()
        assert user.email_confirmado is True

    def test_confirmar_email_nao_duplica(self):
        user = Usuario(email="teste@teste.com", email_confirmado=True)
        user.confirmar_email()
        assert user.email_confirmado is True

    def test_pode_criar_bot_free(self):
        plano = ConfiguracaoPlano(tipo=TipoPlano.FREE)
        user = Usuario(plano=plano)
        assert user.pode_criar_bot()  # max_bots=1 > 0

    def test_registrar_login(self):
        user = Usuario(email="teste@teste.com")
        assert user.ultimo_login is None
        user.registrar_login()
        assert user.ultimo_login is not None

    def test_status_ativo(self):
        user = Usuario(status=StatusUsuario.ATIVO)
        assert user.esta_ativo()

    def test_status_suspenso(self):
        user = Usuario(status=StatusUsuario.SUSPENSO)
        assert not user.esta_ativo()

    def test_upgrade_plano(self):
        user = Usuario(plano=ConfiguracaoPlano(tipo=TipoPlano.FREE))
        assert user.plano.max_bots == 1
        user.plano.upgrade_para(TipoPlano.PRO)
        assert user.plano.max_bots == 10


class TestRegraAutomacao:
    """Testes da entidade RegraAutomacao."""

    def test_criar_regra(self):
        regra = RegraAutomacao(
            bot_id="507f1f77bcf86cd799439011",
            nome="Saudação",
            ativado=True,
        )
        assert regra.nome == "Saudação"
        assert regra.ativado is True
        assert regra.bot_id == "507f1f77bcf86cd799439011"

    def test_avaliar_condicao_keyword_contains(self):
        condicao = Condicao(
            tipo=TipoCondicao.KEYWORD,
            campo="message.content",
            operador=OperadorCondicao.CONTEM,
            valor="olá",
        )
        contexto = {"message": {"content": "Olá, como vai?"}}
        assert condicao.avaliar(contexto) is True

    def test_avaliar_condicao_keyword_not_contains(self):
        condicao = Condicao(
            tipo=TipoCondicao.KEYWORD,
            campo="message.content",
            operador=OperadorCondicao.CONTEM,
            valor="tchau",
        )
        contexto = {"message": {"content": "Olá, como vai?"}}
        assert condicao.avaliar(contexto) is False

    def test_avaliar_condicao_negar(self):
        condicao = Condicao(
            tipo=TipoCondicao.KEYWORD,
            campo="message.content",
            operador=OperadorCondicao.CONTEM,
            valor="tchau",
            negar=True,
        )
        contexto = {"message": {"content": "Olá, como vai?"}}
        assert condicao.avaliar(contexto) is True  # negado

    def test_regra_ativar_desativar(self):
        regra = RegraAutomacao(nome="Teste")
        assert regra.esta_ativado()
        regra.desativar()
        assert not regra.esta_ativado()
        regra.ativar()
        assert regra.esta_ativado()

    def test_regra_pode_executar(self):
        regra = RegraAutomacao(
            nome="Teste",
            limite_por_conversa=1,
        )
        assert regra.pode_executar("conv-1")

    def test_regra_limite_conversa(self):
        regra = RegraAutomacao(
            nome="Teste",
            limite_por_conversa=1,
        )
        regra.executar("conv-1")
        assert not regra.pode_executar("conv-1")  # já executou
        assert regra.pode_executar("conv-2")  # outra conversa

    def test_avaliar_multiplas_condicoes_or(self):
        regra = RegraAutomacao(
            nome="Teste",
            condicoes=[
                Condicao(tipo=TipoCondicao.KEYWORD, operador=OperadorCondicao.CONTEM, valor="preço"),
                Condicao(tipo=TipoCondicao.KEYWORD, operador=OperadorCondicao.CONTEM, valor="valor"),
            ],
        )
        # OR — uma das condições basta
        assert regra.avaliar_condicoes({"message": {"content": "Qual o preço?"}})
        assert regra.avaliar_condicoes({"message": {"content": "Qual o valor?"}})
        assert not regra.avaliar_condicoes({"message": {"content": "Olá"}})


class TestConfiguracaoPlano:
    """Testes da configuração de plano."""

    def test_plano_free_limits(self):
        plano = ConfiguracaoPlano(tipo=TipoPlano.FREE)
        assert plano.max_bots == 1
        assert plano.max_mensagens_por_mes == 100

    def test_plano_pro_limits(self):
        plano = ConfiguracaoPlano(tipo=TipoPlano.FREE)
        plano.upgrade_para(TipoPlano.PRO)
        assert plano.max_bots == 10
        assert plano.max_mensagens_por_mes == 50000

    def test_tem_feature(self):
        plano = ConfiguracaoPlano(tipo=TipoPlano.FREE)
        plano.upgrade_para(TipoPlano.PRO)
        assert plano.tem_feature("api_access")
        assert not plano.tem_feature("whitelabel")

    def test_trial(self):
        from datetime import datetime, timedelta
        plano = ConfiguracaoPlano()
        plano.trial_termina_em = datetime.utcnow() + timedelta(days=7)
        assert plano.is_trial()
        assert not plano.trial_expirado()
