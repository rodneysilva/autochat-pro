"""
Endpoint de chat streaming (SSE).

Para teste manual de LLM via dashboard.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional

from src.api.middleware.auth import get_current_user
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role da mensagem (user ou assistant)")
    content: str = Field(..., description="Conteúdo da mensagem")


class ChatStreamRequest(BaseModel):
    """Request para chat streaming."""

    provider: str = Field("glm", description="Provedor LLM (glm, openai, anthropic, ollama)")
    model: str = Field("glm-4-flash", description="Modelo LLM")
    messages: List[ChatMessage] = Field(..., description="Mensagens da conversa")
    system_prompt: Optional[str] = Field(None, description="Prompt do sistema")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Temperatura")
    max_tokens: int = Field(2048, ge=1, le=8192, description="Máximo de tokens")


class ChatNonStreamRequest(BaseModel):
    """Request para chat non-streaming."""

    provider: str = Field("glm", description="Provedor LLM")
    model: str = Field("glm-4-flash", description="Modelo LLM")
    messages: List[ChatMessage] = Field(..., description="Mensagens da conversa")
    system_prompt: Optional[str] = Field(None, description="Prompt do sistema")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Temperatura")
    max_tokens: int = Field(2048, ge=1, le=8192, description="Máximo de tokens")


@router.post("/stream")
async def chat_stream(
    request: ChatStreamRequest,
    current_user=Depends(get_current_user),
):
    """Stream de resposta LLM via SSE (Server-Sent Events)."""

    from src.infrastructure.external_services.llm.llm_service import LLMProvider, get_llm_service

    try:
        provider = LLMProvider(request.provider)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail={"erro": {"codigo": "INVALID_PROVIDER", "mensagem": f"Provedor inválido: {request.provider}"}},
        )

    llm = get_llm_service()
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    async def event_generator():
        try:
            async for token in llm.chat_stream(
                provider=provider,
                model=request.model,
                messages=messages,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Erro no stream: {e}")
            error_msg = str(e).replace("\n", " ")
            yield f"event: error\ndata: {error_msg}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/complete")
async def chat_complete(
    request: ChatNonStreamRequest,
    current_user=Depends(get_current_user),
):
    """Chat completion não-streaming (resposta completa)."""

    from src.infrastructure.external_services.llm.llm_service import LLMProvider, get_llm_service
    from fastapi import HTTPException

    try:
        provider = LLMProvider(request.provider)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"erro": {"codigo": "INVALID_PROVIDER", "mensagem": f"Provedor inválido: {request.provider}"}},
        )

    llm = get_llm_service()
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    try:
        response = await llm.chat(
            provider=provider,
            model=request.model,
            messages=messages,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return {"resposta": response}
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(
            status_code=500,
            detail={"erro": {"codigo": "LLM_ERROR", "mensagem": str(e)}},
        )


@router.get("/providers")
async def list_providers(
    current_user=Depends(get_current_user),
):
    """Lista provedores LLM disponíveis e modelos."""
    from src.infrastructure.external_services.llm.llm_service import LLMProvider, AVAILABLE_MODELS

    providers = []
    for p in LLMProvider:
        providers.append({
            "id": p.value,
            "nome": p.value.upper(),
            "modelos": AVAILABLE_MODELS.get(p, []),
        })
    return {"providers": providers}
