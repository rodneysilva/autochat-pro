"""
Serviço de contexto de conversa para LLM.

Gerencia o histórico de mensagens para construir o contexto da janela do LLM.
"""

from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

# Estimativa: ~4 caracteres por token (conservador)
CHARS_PER_TOKEN = 4

# Mapeamento de papel para role do LLM
ROLE_MAP = {
    "user": "user",
    "bot": "assistant",
    "human": "assistant",
    "system": "system",
}


class ConversationContextService:
    """Gerencia histórico de conversa para contexto LLM."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._db = database
        self._messages = database.messages

    async def get_context_messages(
        self,
        conversation_id: str,
        bot_system_prompt: str,
        bot_name: str = "",
        business_context: str = "",
        max_tokens: int = 3000,
        max_messages: int = 20,
    ) -> list:
        """
        Constrói contexto de mensagens para o LLM.

        1. Últimas N mensagens da conversa (inbound + outbound)
        2. Trunca para caber em max_tokens
        3. Retorna lista formatada para o LLM

        Args:
            conversation_id: ID da conversa (ObjectId string).
            bot_system_prompt: Prompt do sistema configurado no bot.
            bot_name: Nome do bot (para personalização).
            business_context: Contexto adicional do negócio.
            max_tokens: Limite máximo de tokens do contexto.
            max_messages: Máximo de mensagens históricas.

        Returns:
            Lista de dicionários: [{"role": "user"|"assistant", "content": "..."}]
        """
        try:
            # Buscar últimas mensagens da conversa
            cursor = self._messages.find(
                {"conversation_id": ObjectId(conversation_id)}
            ).sort("created_at", -1).limit(max_messages)

            docs = await cursor.to_list(length=max_messages)

            if not docs:
                return []

            # Processar de trás para frente (mais recentes primeiro = manter)
            llm_messages = []
            total_chars = 0
            max_chars = max_tokens * CHARS_PER_TOKEN

            for doc in reversed(docs):
                role = ROLE_MAP.get(doc.get("role", "user"), "user")
                content = doc.get("content", "")
                if not content:
                    continue

                msg_chars = len(content)

                # Verificar se cabe no limite
                if total_chars + msg_chars > max_chars:
                    remaining = max_chars - total_chars
                    if remaining > 20:
                        content = content[:remaining] + "..."
                        llm_messages.append({"role": role, "content": content})
                    break

                total_chars += msg_chars
                llm_messages.append({"role": role, "content": content})

            estimated_tokens = total_chars // CHARS_PER_TOKEN
            logger.info(
                f"Contexto construído: {len(llm_messages)} mensagens, "
                f"~{estimated_tokens} tokens estimados"
            )

            return llm_messages

        except Exception as e:
            logger.error(f"Erro ao construir contexto: {e}", exc_info=True)
            return []

    def build_system_prompt(
        self,
        base_prompt: str,
        bot_name: str = "",
        business_context: str = "",
    ) -> str:
        """
        Monta o prompt do sistema completo.

        Args:
            base_prompt: Prompt base configurado no bot.
            bot_name: Nome do bot.
            business_context: Contexto adicional.

        Returns:
            Prompt do sistema enriquecido.
        """
        parts = []

        if bot_name:
            parts.append(f"Você é o assistente virtual '{bot_name}'.")

        if base_prompt:
            parts.append(base_prompt)

        if business_context:
            parts.append(f"\nContexto adicional: {business_context}")

        parts.append(
            "\nRegras:\n"
            "- Responda sempre em português brasileiro\n"
            "- Seja cordial e profissional\n"
            "- Respostas curtas e diretas (WhatsApp)"
        )

        return "\n".join(parts)


# ========================================
# Singleton
# ========================================

_context_service: Optional[ConversationContextService] = None


def get_context_service() -> Optional[ConversationContextService]:
    """Retorna instância global do ConversationContextService."""
    return _context_service


def init_context_service(database: AsyncIOMotorDatabase) -> ConversationContextService:
    """Inicializa o ConversationContextService global."""
    global _context_service
    _context_service = ConversationContextService(database)
    return _context_service
