"""
Caso de uso para atualização de bot.
"""

from uuid import UUID

from src.domain.repositories.bot_repository import BotRepository
from datetime import datetime
from src.application.dto.bot_dto import AtualizarBotRequest, BotResponse, bot_to_response
from src.shared.exceptions import EntityNotFoundException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class UpdateBotUseCase:
    """Caso de uso para atualização de bot."""

    def __init__(self, bot_repository: BotRepository):
        self._repository = bot_repository

    async def execute(
        self,
        bot_id: str,
        request: AtualizarBotRequest,
        usuario_id: str,
    ) -> BotResponse:
        """Atualiza configuração de um bot."""
        bot = await self._repository.buscar_por_id(bot_id)

        if not bot:
            raise EntityNotFoundException("Bot", bot_id)

        if str(bot.usuario_id) != usuario_id:
            raise EntityNotFoundException("Bot", bot_id)

        # Aplica atualizações parciais
        if request.nome is not None:
            bot.nome = request.nome
        if request.mensagem_boas_vindas is not None:
            bot.mensagem_boas_vindas = request.mensagem_boas_vindas
        if request.mensagem_despedida is not None:
            bot.mensagem_despedida = request.mensagem_despedida
        if request.mensagem_resposta_padrao is not None:
            bot.mensagem_resposta_padrao = request.mensagem_resposta_padrao

        # Working Hours
        if request.working_hours_ativado is not None:
            bot.working_hours.ativado = request.working_hours_ativado
        if request.working_hours_inicio is not None:
            bot.working_hours.inicio = request.working_hours_inicio
        if request.working_hours_fim is not None:
            bot.working_hours.fim = request.working_hours_fim
        if request.working_hours_timezone is not None:
            bot.working_hours.timezone = request.working_hours_timezone
        if request.working_hours_mensagem_fora is not None:
            bot.working_hours.mensagem_fora_horario = request.working_hours_mensagem_fora

        # LLM Config
        if request.llm_ativado is not None:
            bot.llm_config.ativado = request.llm_ativado
        if request.llm_provider is not None:
            bot.llm_config.provider = request.llm_provider
        if request.llm_modelo is not None:
            bot.llm_config.modelo = request.llm_modelo
        if request.llm_temperatura is not None:
            bot.llm_config.temperatura = request.llm_temperatura
        if request.llm_max_tokens is not None:
            bot.llm_config.max_tokens = request.llm_max_tokens
        if request.llm_system_prompt is not None:
            bot.llm_config.system_prompt = request.llm_system_prompt
        if request.llm_max_context_messages is not None:
            bot.llm_config.max_context_messages = request.llm_max_context_messages

        # Telegram Config
        if request.telegram_bot_token is not None:
            bot.telegram_config.bot_token = request.telegram_bot_token
        if request.telegram_bot_username is not None:
            bot.telegram_config.bot_username = request.telegram_bot_username

        bot.atualizado_em = datetime.utcnow()

        updated_bot = await self._repository.salvar(bot)
        logger.info(f"Bot atualizado: {updated_bot.nome} ({bot_id})")

        return bot_to_response(updated_bot)
