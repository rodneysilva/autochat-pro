"""
Serviço unificado de LLM multi-provider.

Suporta: GLM (Z.AI), OpenAI, Anthropic (Claude) e Ollama (local).
"""

from enum import Enum
from typing import AsyncGenerator, List, Optional

import httpx

from src.shared.config import settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class LLMProvider(str, Enum):
    """Provedores LLM suportados."""
    GLM = "glm"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


# Modelos padrão por provider
DEFAULT_MODELS = {
    LLMProvider.GLM: "glm-4.5-air",
    LLMProvider.OPENAI: "gpt-4o-mini",
    LLMProvider.ANTHROPIC: "claude-sonnet-4-20250514",
    LLMProvider.OLLAMA: "llama3",
}

# Modelos disponíveis por provider (para dropdown)
AVAILABLE_MODELS = {
    LLMProvider.GLM: ["glm-4.5-air", "glm-4.5", "glm-4.6", "glm-4.7", "glm-5", "glm-5-turbo", "glm-5.1"],
    LLMProvider.OPENAI: ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    LLMProvider.ANTHROPIC: [
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307",
    ],
    LLMProvider.OLLAMA: ["llama3", "llama3.1", "mistral", "gemma2", "phi3", "qwen2"],
}


class LLMService:
    """Serviço unificado multi-provider LLM."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """Fecha o cliente HTTP."""
        await self._client.aclose()

    # ========================================
    # Chat (non-streaming)
    # ========================================

    async def chat(
        self,
        provider: LLMProvider,
        model: str,
        messages: list,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Envia chat completion e retorna texto da resposta.

        Args:
            provider: Provedor LLM.
            model: Nome do modelo.
            messages: Lista de mensagens [{"role": "user"|"assistant", "content": "..."}].
            system_prompt: Prompt do sistema (injetado como primeira mensagem).
            temperature: Temperatura (0.0-1.0).
            max_tokens: Máximo de tokens na resposta.

        Returns:
            Texto da resposta do modelo.
        """
        if provider == LLMProvider.GLM:
            return await self._chat_glm(model, messages, system_prompt, temperature, max_tokens)
        elif provider == LLMProvider.OPENAI:
            return await self._chat_openai(model, messages, system_prompt, temperature, max_tokens)
        elif provider == LLMProvider.ANTHROPIC:
            return await self._chat_anthropic(model, messages, system_prompt, temperature, max_tokens)
        elif provider == LLMProvider.OLLAMA:
            return await self._chat_ollama(model, messages, system_prompt, temperature)
        else:
            raise ValueError(f"Provedor LLM não suportado: {provider}")

    # ========================================
    # Chat (streaming)
    # ========================================

    async def chat_stream(
        self,
        provider: LLMProvider,
        model: str,
        messages: list,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """
        Stream de tokens da resposta LLM.

        Yields:
            Tokens (strings) conforme chegam.
        """
        if provider == LLMProvider.GLM:
            async for token in self._stream_glm(model, messages, system_prompt, temperature, max_tokens):
                yield token
        elif provider == LLMProvider.OPENAI:
            async for token in self._stream_openai(model, messages, system_prompt, temperature, max_tokens):
                yield token
        elif provider == LLMProvider.ANTHROPIC:
            async for token in self._stream_anthropic(model, messages, system_prompt, temperature, max_tokens):
                yield token
        elif provider == LLMProvider.OLLAMA:
            async for token in self._stream_ollama(model, messages, system_prompt, temperature):
                yield token
        else:
            raise ValueError(f"Provedor LLM não suportado: {provider}")

    # ========================================
    # GLM (OpenAI-compatible)
    # ========================================

    def _glm_url(self) -> str:
        url = settings.LLM_API_URL
        if not url:
            raise Exception("LLM_API_URL não configurada. Defina a variável de ambiente.")
        return url.rstrip("/")

    def _glm_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if settings.LLM_API_KEY:
            headers["Authorization"] = f"Bearer {settings.LLM_API_KEY}"
        return headers

    async def _chat_glm(self, model, messages, system_prompt, temperature, max_tokens):
        full_messages = self._build_messages(messages, system_prompt)
        payload = {
            "model": model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        try:
            resp = await self._client.post(
                f"{self._glm_url()}/chat/completions",
                headers=self._glm_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro GLM: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Erro na API GLM: status {e.response.status_code}")
        except Exception as e:
            logger.error(f"Erro GLM: {e}")
            raise

    async def _stream_glm(self, model, messages, system_prompt, temperature, max_tokens):
        full_messages = self._build_messages(messages, system_prompt)
        payload = {
            "model": model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with self._client.stream(
            "POST",
            f"{self._glm_url()}/chat/completions",
            headers=self._glm_headers(),
            json=payload,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    import json
                    try:
                        chunk = json.loads(line[6:])
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, IndexError, KeyError):
                        continue

    # ========================================
    # OpenAI
    # ========================================

    def _openai_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        key = settings.OPENAI_API_KEY
        if not key:
            raise Exception("OPENAI_API_KEY não configurada.")
        headers["Authorization"] = f"Bearer {key}"
        return headers

    async def _chat_openai(self, model, messages, system_prompt, temperature, max_tokens):
        full_messages = self._build_messages(messages, system_prompt)
        payload = {
            "model": model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            resp = await self._client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self._openai_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro OpenAI: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Erro na API OpenAI: status {e.response.status_code}")
        except Exception as e:
            logger.error(f"Erro OpenAI: {e}")
            raise

    async def _stream_openai(self, model, messages, system_prompt, temperature, max_tokens):
        full_messages = self._build_messages(messages, system_prompt)
        payload = {
            "model": model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with self._client.stream(
            "POST",
            "https://api.openai.com/v1/chat/completions",
            headers=self._openai_headers(),
            json=payload,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    import json
                    try:
                        chunk = json.loads(line[6:])
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, IndexError, KeyError):
                        continue

    # ========================================
    # Anthropic
    # ========================================

    def _anthropic_headers(self) -> dict:
        key = settings.ANTHROPIC_API_KEY
        if not key:
            raise Exception("ANTHROPIC_API_KEY não configurada.")
        return {
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "anthropic-dangerous-direct-browser-access": "true",
        }

    async def _chat_anthropic(self, model, messages, system_prompt, temperature, max_tokens):
        payload = {
            "model": model,
            "messages": messages,  # Anthropic não usa system no messages
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = await self._client.post(
                "https://api.anthropic.com/v1/messages",
                headers=self._anthropic_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            # Anthropic retorna content como lista de blocos
            for block in data.get("content", []):
                if block.get("type") == "text":
                    return block["text"]
            return ""
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro Anthropic: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Erro na API Anthropic: status {e.response.status_code}")
        except Exception as e:
            logger.error(f"Erro Anthropic: {e}")
            raise

    async def _stream_anthropic(self, model, messages, system_prompt, temperature, max_tokens):
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with self._client.stream(
            "POST",
            "https://api.anthropic.com/v1/messages",
            headers=self._anthropic_headers(),
            json=payload,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    import json
                    try:
                        event = json.loads(line[6:])
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            if delta.get("type") == "text_delta":
                                text = delta.get("text", "")
                                if text:
                                    yield text
                    except (json.JSONDecodeError, KeyError):
                        continue

    # ========================================
    # Ollama (local)
    # ========================================

    def _ollama_url(self) -> str:
        return settings.OLLAMA_URL.rstrip("/") if settings.OLLAMA_URL else "http://localhost:11434"

    async def _chat_ollama(self, model, messages, system_prompt, temperature, max_tokens=None):
        full_messages = self._build_messages(messages, system_prompt)
        payload = {
            "model": model,
            "messages": full_messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            resp = await self._client.post(
                f"{self._ollama_url()}/api/chat",
                json=payload,
                timeout=120.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
        except httpx.ConnectError:
            raise Exception("Não foi possível conectar ao Ollama. Verifique se está rodando em localhost:11434")
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro Ollama: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Erro no Ollama: status {e.response.status_code}")
        except Exception as e:
            logger.error(f"Erro Ollama: {e}")
            raise

    async def _stream_ollama(self, model, messages, system_prompt, temperature, max_tokens=None):
        full_messages = self._build_messages(messages, system_prompt)
        payload = {
            "model": model,
            "messages": full_messages,
            "stream": True,
            "options": {"temperature": temperature},
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        async with self._client.stream(
            "POST",
            f"{self._ollama_url()}/api/chat",
            json=payload,
            timeout=120.0,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                import json
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield content
                    # Ollama envia done=true no último chunk
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue

    # ========================================
    # Helpers
    # ========================================

    def _build_messages(self, messages: list, system_prompt: str = None) -> list:
        """Consta lista de mensagens com system prompt opcional."""
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        result.extend(messages)
        return result


# ========================================
# Singleton
# ========================================

_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Retorna instância singleton do LLMService."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def init_llm_service() -> LLMService:
    """Inicializa o LLMService global."""
    global _llm_service
    _llm_service = LLMService()
    return _llm_service


def close_llm_service():
    """Fecha o LLMService."""
    global _llm_service
    if _llm_service:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(_llm_service.close())
            else:
                loop.run_until_complete(_llm_service.close())
        except RuntimeError:
            pass
        _llm_service = None
