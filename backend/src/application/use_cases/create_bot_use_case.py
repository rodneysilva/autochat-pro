"""
Caso de uso para criacao de bot.

Cria um novo bot vinculado ao usuario apos conexao WhatsApp.
"""

from src.domain.entities.bot import Bot, TipoBot, StatusBot
from src.domain.repositories.bot_repository import BotRepository
from src.domain.repositories.user_repository import UserRepository
from src.application.dto.bot_dto import CriarBotRequest, BotResponse
from src.shared.exceptions import ValidationException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class CreateBotUseCase:
    """Caso de uso para criacao de bots."""

    def __init__(self, bot_repository: BotRepository, user_repository: UserRepository = None):
        self._repository = bot_repository
        self._user_repository = user_repository

    async def execute(
        self,
        request: CriarBotRequest,
        usuario_id: str,
    ) -> BotResponse:
        """Cria um novo bot para o usuario."""
        logger.info(f"Criando bot '{request.nome}' para usuario {usuario_id}")

        # Buscar plano do usuario e verificar limite
        max_bots = 1  # default free
        if self._user_repository:
            user = await self._user_repository.find_by_id(usuario_id)
            if user:
                max_bots = user.plano.max_bots

        total_bots = await self._repository.contar_por_usuario(usuario_id)
        if total_bots >= max_bots:
            raise ValidationException(
                f"Voce atingiu o limite de {max_bots} bots do seu plano. Faca upgrade para criar mais.",
                field="nome",
            )

        # Criar entidade
        initial_status = StatusBot.ATIVO if request.tipo.lower() == 'telegram' else StatusBot.CONECTANDO
        bot = Bot(
            nome=request.nome,
            tipo=TipoBot(request.tipo.lower()),
            status=initial_status,
            mensagem_boas_vindas=request.mensagem_boas_vindas or "Olá! Sou seu assistente virtual. Como posso ajudar?",
            mensagem_despedida=request.mensagem_despedida or "Obrigado pelo contato!",
        )
        bot.usuario_id = usuario_id

        # Salvar
        created_bot = await self._repository.salvar(bot)

        logger.info(f"Bot criado: {created_bot.nome} ({created_bot.id})")
        from src.application.dto.bot_dto import bot_to_response
        return bot_to_response(created_bot)

    # Removido _to_response local — usa bot_to_response do dto
