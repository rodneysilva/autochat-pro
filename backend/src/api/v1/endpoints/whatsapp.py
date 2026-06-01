"""
Endpoints de integração WhatsApp.

Gerencia instâncias WhatsApp, QR Code, conexão por telefone e envio de mensagens.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List

from src.infrastructure.external_services.whatsapp import (
    EvolutionWhatsAppService,
    WhatsAppConnectionStatus,
    get_whatsapp_service,
)
from src.api.middleware.auth import get_current_user
from src.shared.exceptions import BaseAppException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


# ========================================
# Request/Response Models
# ========================================

class CreateInstanceRequest(BaseModel):
    """Request para criar instância WhatsApp."""
    name: str = Field(..., min_length=3, max_length=50, description="Nome único da instância")
    qrcode: bool = Field(default=True, description="Gerar QR Code para conexão")


class ConnectWithPhoneRequest(BaseModel):
    """Request para conexão por número."""
    instance_name: str = Field(..., description="Nome da instância")
    phone_number: str = Field(..., min_length=10, max_length=15, description="Número com DDI")


class SendTextRequest(BaseModel):
    """Request para enviar texto."""
    instance_name: str = Field(..., description="Nome da instância")
    phone_number: str = Field(..., min_length=10, max_length=15, description="Número destinatário")
    message: str = Field(..., min_length=1, max_length=4096, description="Conteúdo da mensagem")
    delay: int = Field(default=1000, ge=0, le=10000, description="Delay em ms")


class SendMediaRequest(BaseModel):
    """Request para enviar mídia."""
    instance_name: str = Field(..., description="Nome da instância")
    phone_number: str = Field(..., description="Número destinatário")
    media_url: str = Field(..., description="URL da mídia")
    caption: Optional[str] = Field(None, max_length=1000, description="Legenda")
    media_type: str = Field(default="image", description="Tipo: image, video, audio, document")


class SetWebhookRequest(BaseModel):
    """Request para configurar webhook."""
    webhook_url: str = Field(..., description="URL do webhook")
    events: List[str] = Field(default=["messages"], description="Eventos desejados")
    webhook_by_events: bool = Field(default=False, description="Separar webhooks por evento")


class InstanceResponse(BaseModel):
    """Response com dados da instância."""
    name: str
    status: WhatsAppConnectionStatus
    qrcode: Optional[str] = None
    phone_connected: Optional[str] = None
    created_at: Optional[str] = None


class MessageResponse(BaseModel):
    """Response de envio de mensagem."""
    message_id: str
    status: str
    timestamp: str


# ========================================
# Dependencies
# ========================================

async def get_whatsapp() -> EvolutionWhatsAppService:
    """Obtém instância do serviço WhatsApp."""
    return get_whatsapp_service()


# ========================================
# Endpoints - Instância Management
# ========================================

@router.post(
    "/instances",
    response_model=InstanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar instância WhatsApp",
    description="Cria uma nova instância (bot) WhatsApp com ou sem QR Code.",
)
async def create_instance(
    request: CreateInstanceRequest,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """
    Cria uma nova instância WhatsApp.

    - **name**: Nome único da instância (3-50 caracteres)
    - **qrcode**: Se True, gera QR Code; se False, use phone pairing
    """
    try:
        result = await whatsapp.create_instance(request.name, qrcode=request.qrcode)

        # Se QR Code foi solicitado, obter o código
        qrcode = None
        if request.qrcode:
            qrcode = await whatsapp.get_qr_code(request.name)

        return InstanceResponse(
            name=request.name,
            status=await whatsapp.get_instance_status(request.name),
            qrcode=qrcode,
        )
    except BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao criar instância: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao criar instância"}}
        )


@router.get(
    "/instances",
    summary="Listar instâncias",
    description="Lista todas as instâncias WhatsApp criadas.",
)
async def list_instances(
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Lista todas as instâncias do usuário."""
    try:
        instances = await whatsapp.list_instances()
        return {"instances": instances}
    except Exception as e:
        logger.error(f"Erro ao listar instâncias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao listar instâncias"}}
        )


@router.get(
    "/instances/{instance_name}",
    response_model=InstanceResponse,
    summary="Obter instância",
    description="Obtém informações de uma instância específica.",
)
async def get_instance(
    instance_name: str,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Obtém informações de uma instância."""
    try:
        status_result = await whatsapp.get_instance_status(instance_name)
        info = await whatsapp.get_instance_info(instance_name)

        return InstanceResponse(
            name=instance_name,
            status=status_result,
            qrcode=await whatsapp.get_qr_code(instance_name),
        )
    except Exception as e:
        logger.error(f"Erro ao obter instância: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Instância não encontrada"}}
        )


@router.delete(
    "/instances/{instance_name}",
    summary="Deletar instância",
    description="Remove uma instância WhatsApp.",
)
async def delete_instance(
    instance_name: str,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Remove uma instância."""
    try:
        await whatsapp.delete_instance(instance_name)
        return {"message": f"Instância {instance_name} removida com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao deletar instância: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao deletar instância"}}
        )


@router.post(
    "/instances/{instance_name}/logout",
    summary="Logout da instância",
    description="Desconecta a instância (mantém os dados).",
)
async def logout_instance(
    instance_name: str,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Faz logout da instância."""
    try:
        await whatsapp.logout(instance_name)
        return {"message": f"Logout realizado na instância {instance_name}"}
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao fazer logout"}}
        )


# ========================================
# Endpoints - QR Code Connection
# ========================================

@router.post(
    "/connect/qrcode",
    response_model=InstanceResponse,
    summary="Conectar via QR Code",
    description="Inicia conexão WhatsApp gerando QR Code.",
)
async def connect_with_qrcode(
    request: CreateInstanceRequest,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """
    Conecta WhatsApp via QR Code.

    Retorna o QR Code que deve ser escaneado no WhatsApp mobile.
    """
    try:
        result = await whatsapp.connect_with_qr(request.name)
        qrcode = await whatsapp.get_qr_code(request.name)

        return InstanceResponse(
            name=request.name,
            status=await whatsapp.get_instance_status(request.name),
            qrcode=qrcode,
        )
    except Exception as e:
        logger.error(f"Erro ao conectar via QR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao gerar QR Code"}}
        )


@router.get(
    "/instances/{instance_name}/qrcode",
    summary="Obter QR Code",
    description="Obtém o QR Code atual da instância.",
)
async def get_qrcode(
    instance_name: str,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Obtém o QR Code da instância."""
    try:
        qrcode = await whatsapp.get_qr_code(instance_name)

        if not qrcode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"erro": {"codigo": "NO_QRCODE", "mensagem": "QR Code não disponível"}}
            )

        return {"instance": instance_name, "qrcode": qrcode}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter QR Code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao obter QR Code"}}
        )


# ========================================
# Endpoints - Phone Number Connection
# ========================================

@router.post(
    "/connect/phone",
    summary="Conectar via telefone",
    description="Inicia conexão usando número de telefone (code pairing).",
)
async def connect_with_phone(
    request: ConnectWithPhoneRequest,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """
    Conecta WhatsApp via número de telefone.

    Retorna um código que deve ser inserido no WhatsApp:
    1. Abra WhatsApp > Dispositivos conectados
    2. Toque em "Vincular um telefone"
    3. Digite o código fornecido
    """
    try:
        result = await whatsapp.connect_with_phone(
            request.instance_name,
            request.phone_number
        )

        pairing_code = result.get("pairingCode", result.get("code", ""))
        if not pairing_code:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"erro": {"codigo": "PAIRING_FAILED", "mensagem": "Não foi possível gerar o código de pareamento. Tente novamente."}}
            )

        return {
            "instance": request.instance_name,
            "message": "Código de pareamento gerado. Use no WhatsApp mobile.",
            "pairing_code": pairing_code,
            "status": await whatsapp.get_instance_status(request.instance_name),
        }
    except Exception as e:
        logger.error(f"Erro ao conectar via telefone: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao conectar via telefone"}}
        )


@router.get(
    "/instances/{instance_name}/phone/status",
    summary="Status conexão telefone",
    description="Verifica status do pareamento por telefone.",
)
async def check_phone_status(
    instance_name: str,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Verifica status do pareamento por telefone."""
    try:
        status_info = await whatsapp.check_phone_pairing(instance_name)
        return {
            "instance": instance_name,
            "status": await whatsapp.get_instance_status(instance_name),
            "details": status_info,
        }
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao verificar status"}}
        )


# ========================================
# Endpoints - Messaging
# ========================================

@router.post(
    "/send/text",
    summary="Enviar texto",
    description="Envia mensagem de texto WhatsApp.",
)
async def send_text(
    request: SendTextRequest,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Envia mensagem de texto."""
    try:
        # Formatar número
        phone = whatsapp.format_phone_number(request.phone_number)

        result = await whatsapp.send_text(
            request.instance_name,
            phone,
            request.message,
            request.delay,
        )

        return {
            "message": "Mensagem enviada com sucesso",
            "message_id": result.get("key", {}).get("id"),
        }
    except Exception as e:
        logger.error(f"Erro ao enviar texto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao enviar mensagem"}}
        )


@router.post(
    "/send/media",
    summary="Enviar mídia",
    description="Envia mensagem com mídia (imagem, vídeo, áudio, documento).",
)
async def send_media(
    request: SendMediaRequest,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Envia mensagem com mídia."""
    try:
        phone = whatsapp.format_phone_number(request.phone_number)

        result = await whatsapp.send_media(
            request.instance_name,
            phone,
            request.media_url,
            request.caption,
            request.media_type,
        )

        return {
            "message": "Mídia enviada com sucesso",
            "message_id": result.get("key", {}).get("id"),
        }
    except Exception as e:
        logger.error(f"Erro ao enviar mídia: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao enviar mídia"}}
        )


@router.get(
    "/instances/{instance_name}/messages",
    summary="Obter mensagens",
    description="Obtém mensagens recebidas pela instância.",
)
async def get_messages(
    instance_name: str,
    limit: int = 100,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Obtém mensagens da instância."""
    try:
        messages = await whatsapp.get_messages(instance_name, limit)
        return {"instance": instance_name, "messages": messages}
    except Exception as e:
        logger.error(f"Erro ao obter mensagens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao obter mensagens"}}
        )


# ========================================
# Endpoints - Webhook
# ========================================

@router.post(
    "/instances/{instance_name}/webhook",
    summary="Configurar webhook",
    description="Configura webhook para receber eventos da instância.",
)
async def set_webhook(
    instance_name: str,
    request: SetWebhookRequest,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Configura webhook da instância."""
    try:
        await whatsapp.set_webhook(
            instance_name,
            request.webhook_url,
            request.events,
            request.webhook_by_events,
        )

        return {"message": f"Webhook configurado para {instance_name}"}
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao configurar webhook"}}
        )


@router.get(
    "/instances/{instance_name}/webhook",
    summary="Obter webhook",
    description="Obtém configuração de webhook da instância.",
)
async def get_webhook(
    instance_name: str,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Obtém webhook da instância."""
    try:
        webhook = await whatsapp.get_webhook(instance_name)
        return {"instance": instance_name, "webhook": webhook}
    except Exception as e:
        logger.error(f"Erro ao obter webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao obter webhook"}}
        )


# ========================================
# Endpoints - Status
# ========================================

@router.get(
    "/instances/{instance_name}/status",
    summary="Status da instância",
    description="Obtém status atual da conexão WhatsApp.",
)
async def get_instance_status(
    instance_name: str,
    whatsapp: EvolutionWhatsAppService = Depends(get_whatsapp),
    current_user = Depends(get_current_user),
):
    """Obtém status da instância."""
    try:
        conn_status = await whatsapp.get_instance_status(instance_name)

        return {
            "instance": instance_name,
            "status": conn_status,
            "connected": conn_status == WhatsAppConnectionStatus.CONNECTED,
        }
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao obter status"}}
        )


# ========================================
# Webhook Receiver (Para Evolution API)
# ========================================

@router.post(
    "/webhook/{instance_name}",
    summary="Receber webhook WhatsApp",
    description="Endpoint que recebe eventos da Evolution API e processa mensagens com IA.",
)
async def receive_webhook(
    instance_name: str,
    event: dict,
):
    """
    Recebe webhooks da Evolution API e processa mensagens automaticamente.

    Eventos possíveis:
    - messages.upsert: Nova mensagem recebida → processa com IA
    - messages.update: Status da mensagem (entregue, lido, etc.)
    - presence: Presença do contato

    Este endpoint NÃO exige autenticação (é callback da Evolution API).
    """
    event_type = event.get("event", "unknown")
    logger.info(f"Webhook recebido para {instance_name}: {event_type}")

    # Processar mensagens novas (Evolution API v2 usa MESSAGES_UPSERT)
    if event_type in ("messages.upsert", "MESSAGES_UPSERT"):
        try:
            from src.application.services.message_processor import get_message_processor

            processor = get_message_processor()
            if processor:
                response_id = await processor.process_incoming_message(
                    instance_name, event
                )
                if response_id:
                    logger.info(
                        f"Webhook processado: resposta enviada (msg_id={response_id})"
                    )
            else:
                logger.warning("MessageProcessor não inicializado")
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}", exc_info=True)

        # Garantir webhook configurado (idempotente)
        try:
            from src.infrastructure.external_services.whatsapp import get_whatsapp_service
            ws = get_whatsapp_service()
            webhook_url = f"http://autochat-backend:8000/api/v1/whatsapp/webhook/{instance_name}"
            # Verificar se webhook já está configurado
            existing = await ws.get_webhook(instance_name)
            if not existing or not existing.get("url"):
                await ws.set_webhook(
                    instance_name,
                    webhook_url,
                    ["MESSAGES_UPSERT"],
                    False,
                )
                logger.info(f"Webhook auto-configurado para {instance_name}: {webhook_url}")
        except Exception as e:
            logger.warning(f"Não foi possível auto-configurar webhook: {e}")

    return {"status": "received", "event": event_type}
