"""
Caso de uso para criação de bot.

Cria um novo bot vinculado ao usuário após conexão WhatsApp.
"""

# uuid not needed - IDs are ObjectId strings

from src.domain.entities.bot import Bot, TipoBot, StatusBot
from src.domain.repositories.bot_repository import BotRepository
from src.application.dto.bot_dto import CriarBotRequest, BotResponse
from src.shared.exceptions import ValidationException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class CreateBotUseCase:
    """Caso de uso para criação de bots."""

    def __init__(self, bot_repository: BotRepository):
        self._repository = bot_repository

    async def execute(
        self,
        request: CriarBotRequest,
        usuario_id: str,
    ) -> BotResponse:
        """Cria um novo bot para o usuário."""
        logger.info(f"Criando bot '{request.nome}' para usuário {usuario_id}")

        # Verificar limite de bots do plano (TODO: buscar plano do usuário)
        total_bots = await self._repository.contar_por_usuario(usuario_id)
        if total_bots >= 10:
            raise ValidationException(
                "Você atingiu o limite de bots do seu plano",
                field="nome",
            )

        # Criar entidade
        bot = Bot(
            nome=request.nome,
            tipo=TipoBot(request.tipo.lower()),
            status=StatusBot.CONECTANDO,
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
