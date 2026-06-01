"""
Serviço de integração com a API GLM (LLM).

Utiliza formato OpenAI-compatible para chamadas à API GLM.
"""

from functools import lru_cache
from typing import List, Optional

import httpx
from src.shared.config import settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class GLMService:
    """Serviço para comunicação com a API GLM."""

    def __init__(self):
        self.api_url = settings.LLM_API_URL
        self.api_key = settings.LLM_API_KEY
        self.default_model = settings.LLM_MODEL
        self.default_temperature = settings.LLM_TEMPERATURE
        self.default_max_tokens = settings.LLM_MAX_TOKENS

    def _get_headers(self) -> dict:
        """Retorna headers para requisição à API."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def chat_completion(
        self,
        messages: List[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Envia mensagens para a API GLM e retorna a resposta.

        Args:
            messages: Lista de mensagens no formato [{"role": "system"|"user"|"assistant", "content": "..."}]
            model: Modelo GLM (glm-4-flash, glm-4, glm-4-plus)
            temperature: Temperatura (0.0 a 1.0)
            max_tokens: Máximo de tokens na resposta

        Returns:
            Texto da resposta do modelo.

        Raises:
            Exception: Se a API não estiver configurada ou retornar erro.
        """
        if not self.api_url:
            raise Exception("LLM_API_URL não configurada. Defina a variável de ambiente.")

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens or self.default_max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )

                if response.status_code != 200:
                    logger.error(
                        f"Erro na API GLM: {response.status_code} - {response.text}"
                    )
                    raise Exception(
                        f"Erro na API GLM: status {response.status_code}"
                    )

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                logger.info(f"Resposta GLM gerada ({len(content)} chars, modelo={payload['model']})")
                return content

        except httpx.TimeoutException:
            logger.error("Timeout ao chamar API GLM")
            raise Exception("Timeout ao chamar API GLM. Tente novamente.")
        except httpx.ConnectError as e:
            logger.error(f"Erro de conexão com API GLM: {e}")
            raise Exception(f"Não foi possível conectar à API GLM: {self.api_url}")
        except KeyError as e:
            logger.error(f"Resposta inesperada da API GLM: {e} - {response.text[:200]}")
            raise Exception("Formato de resposta inesperado da API GLM.")

    async def generate_response(
        self,
        user_message: str,
        system_prompt: str = "",
        conversation_history: Optional[List[dict]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Gera resposta para uma mensagem do usuário.

        Args:
            user_message: Mensagem do usuário.
            system_prompt: Prompt do sistema (instruções do bot).
            conversation_history: Histórico da conversa para contexto.
            model: Modelo GLM.
            temperature: Temperatura.
            max_tokens: Máximo de tokens.

        Returns:
            Texto da resposta gerada.
        """
        messages = []

        # Prompt do sistema
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Histórico da conversa
        if conversation_history:
            messages.extend(conversation_history)

        # Mensagem atual do usuário
        messages.append({"role": "user", "content": user_message})

        return await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )


@lru_cache()
def get_glm_service() -> GLMService:
    """Retorna instância singleton do GLMService."""
    return GLMService()
