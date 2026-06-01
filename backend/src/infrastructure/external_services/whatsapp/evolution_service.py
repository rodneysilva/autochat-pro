"""
Serviço de integração com WhatsApp via Evolution API.

Suporta conexão por QR Code e por número de telefone.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

import httpx
from src.shared.config import settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class WhatsAppConnectionStatus(str, Enum):
    """Status da conexão WhatsApp."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    QR_CODE = "qr_code"
    TIMEOUT = "timeout"
    ERROR = "error"


class EvolutionWhatsAppService:
    """
    Serviço para integração com WhatsApp usando Evolution API.

    Suporta múltiplas instâncias (bots) com conexão por QR Code
    ou emparelhamento por número de telefone.
    """

    def __init__(self):
        """Inicializa o serviço."""
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', 'http://localhost:8080')
        self.api_key = getattr(settings, 'WHATSAPP_API_KEY', '')

    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers com API key."""
        return {
            "Content-Type": "application/json",
            "apikey": self.api_key,
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Faz requisição à Evolution API.

        Args:
            method: Método HTTP (GET, POST, DELETE)
            endpoint: Endpoint da API
            data: Dados para envio (POST)
            params: Parâmetros de query (GET)

        Returns:
            Resposta da API como dicionário.

        Raises:
            Exception: Erro na requisição.
        """
        url = f"{self.api_url}{endpoint}"

        # Timeout maior para operações de mensagem (envio pode demorar)
        timeout = 60.0 if "/message/" in endpoint else 30.0

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=self._get_headers(), params=params)
                elif method == "POST":
                    response = await client.post(url, headers=self._get_headers(), json=data)
                elif method == "DELETE":
                    response = await client.delete(url, headers=self._get_headers())
                elif method == "PUT":
                    response = await client.put(url, headers=self._get_headers(), json=data)
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Erro na requisição: {e}")
            raise

    # ========================================
    # Instância (Bot) Management
    # ========================================

    async def create_instance(
        self,
        instance_name: str,
        qrcode: bool = True,
        integration: str = "WHATSAPP-BAILEYS",
    ) -> Dict[str, Any]:
        """
        Cria uma nova instância (bot) WhatsApp.

        Args:
            instance_name: Nome único da instância.
            qrcode: Se True, gera QR Code para conexão.
            integration: Tipo de integração (WHATSAPP-BAILEYS).

        Returns:
            Dados da instância criada.
        """
        data = {
            "instanceName": instance_name,
            "qrcode": qrcode,
            "integration": integration,
        }

        logger.info(f"Criando instância WhatsApp: {instance_name}")
        return await self._request("POST", "/instance/create", data)

    async def delete_instance(self, instance_name: str) -> Dict[str, Any]:
        """
        Remove uma instância WhatsApp.

        Args:
            instance_name: Nome da instância.

        Returns:
            Confirmação da remoção.
        """
        logger.info(f"Removendo instância: {instance_name}")
        return await self._request("DELETE", f"/instance/delete/{instance_name}")

    async def get_instance_info(self, instance_name: str) -> Dict[str, Any]:
        """
        Obtém informações de uma instância.

        Evolution API v2: GET /instance/connectionState/{instanceName}

        Args:
            instance_name: Nome da instância.

        Returns:
            Dados da instância.
        """
        return await self._request("GET", f"/instance/connectionState/{instance_name}")

    async def list_instances(self) -> List[Dict[str, Any]]:
        """
        Lista todas as instâncias.

        Returns:
            Lista de instâncias.
        """
        return await self._request("GET", "/instance/fetchInstances", params={}, data={})

    async def get_instance_status(
        self,
        instance_name: str,
    ) -> WhatsAppConnectionStatus:
        """
        Obtém status da conexão de uma instância.

        Args:
            instance_name: Nome da instância.

        Returns:
            Status da conexão.
        """
        try:
            info = await self.get_instance_info(instance_name)
            # Evolution API v2 retorna state aninhado em "instance"
            instance_data = info.get("instance", info)
            state = instance_data.get("state", "disconnected")

            # Mapear estados Evolution para nossos enums
            status_map = {
                "close": WhatsAppConnectionStatus.DISCONNECTED,
                "connecting": WhatsAppConnectionStatus.CONNECTING,
                "open": WhatsAppConnectionStatus.CONNECTED,
                "qrcode": WhatsAppConnectionStatus.QR_CODE,
                "timeout": WhatsAppConnectionStatus.TIMEOUT,
            }

            return status_map.get(state, WhatsAppConnectionStatus.ERROR)

        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return WhatsAppConnectionStatus.ERROR

    # ========================================
    # QR Code Connection
    # ========================================

    async def get_qr_code(self, instance_name: str) -> Optional[str]:
        """
        Obtém o QR Code para conexão.

        Na Evolution API v2, o QR Code vem no endpoint /instance/restart/{name}
        ou na criação da instância (/instance/create).

        Args:
            instance_name: Nome da instância.

        Returns:
            Base64 do QR Code (sem prefixo) ou None.
        """
        try:
            # Tentar restart para obter novo QR Code
            result = await self._request("POST", f"/instance/restart/{instance_name}")

            # Evolution API v2 retorna base64 com prefixo data:image/png;base64,...
            base64 = result.get("base64")
            if base64:
                if base64.startswith("data:image"):
                    return base64.split(",")[1]
                return base64

            return None

        except Exception as e:
            logger.error(f"Erro ao obter QR Code: {e}")
            return None

    async def connect_with_qr(self, instance_name: str) -> Dict[str, Any]:
        """
        Inicia conexão via QR Code.

        Args:
            instance_name: Nome da instância.

        Returns:
            Dados da instância com QR Code.
        """
        # Criar ou reconectar instância com QR Code
        try:
            # Primeiro tenta criar
            result = await self.create_instance(instance_name, qrcode=True)
            logger.info(f"Instância {instance_name} criada para conexão QR")
            return result
        except Exception as e:
            # Se já existe, obter QR Code
            logger.info(f"Instância {instance_name} já existe, obtendo QR Code")
            return await self.get_instance_info(instance_name)

    # ========================================
    # Phone Number Connection
    # ========================================

    async def connect_with_phone(
        self,
        instance_name: str,
        phone_number: str,
    ) -> Dict[str, Any]:
        """
        Conecta usando número de telefone (code pairing).

        Evolution API v2: GET /instance/connect/{instanceName}?number={phone_number}

        Se a instância já existir e estiver em estado close/connecting/error,
        ela é deletada e recriada para gerar um novo pairing code.

        Args:
            instance_name: Nome da instância.
            phone_number: Número com DDI (ex: 5511999999999).

        Returns:
            Dados com pairingCode.
        """
        # Verificar se instância já existe e precisa ser recriada
        try:
            existing = await self.list_instances()
            for inst in existing:
                if inst.get("name") == instance_name:
                    state = inst.get("connectionStatus", "")
                    if state in ("close", "connecting", "refused"):
                        logger.info(f"Instância {instance_name} em estado {state}, deletando para recriar")
                        try:
                            await self.delete_instance(instance_name)
                        except Exception:
                            pass
                    break
        except Exception:
            pass  # Seguir sem verificar

        # Criar instância sem QR Code
        try:
            await self.create_instance(instance_name, qrcode=False)
        except Exception:
            pass  # Instância já existe

        # Iniciar pairing por telefone (Evolution API v2 — GET com query param)
        logger.info(f"Iniciando pairing para {instance_name} com telefone {phone_number}")
        result = await self._request(
            "GET",
            f"/instance/connect/{instance_name}",
            params={"number": phone_number},
        )

        return result

    async def check_phone_pairing(
        self,
        instance_name: str,
    ) -> Dict[str, Any]:
        """
        Verifica status do pairing por telefone.

        Evolution API v2: GET /instance/connectionState/{instanceName}

        Args:
            instance_name: Nome da instância.

        Returns:
            Status do pairing.
        """
        return await self._request("GET", f"/instance/connectionState/{instance_name}")

    # ========================================
    # Messaging
    # ========================================

    async def send_text(
        self,
        instance_name: str,
        phone_number: str,
        message: str,
        delay: int = 1000,
    ) -> Dict[str, Any]:
        """
        Envia mensagem de texto.

        Args:
            instance_name: Nome da instância.
            phone_number: Número do destinatário (com DDI, sem +).
            message: Conteúdo da mensagem.
            delay: Delay em milissegundos.

        Returns:
            Confirmação do envio.
        """
        data = {
            "number": phone_number,
            "text": message,
            "delay": delay,
        }

        logger.info(f"Enviando mensagem para {phone_number} via {instance_name}")
        return await self._request("POST", f"/message/sendText/{instance_name}", data)

    async def send_media(
        self,
        instance_name: str,
        phone_number: str,
        media_url: str,
        caption: Optional[str] = None,
        media_type: str = "image",
    ) -> Dict[str, Any]:
        """
        Envia mensagem com mídia.

        Args:
            instance_name: Nome da instância.
            phone_number: Número do destinatário.
            media_url: URL da mídia.
            caption: Legenda da mensagem.
            media_type: Tipo (image, video, audio, document).

        Returns:
            Confirmação do envio.
        """
        data = {
            "number": phone_number,
            "mediatype": media_type,
            "media": media_url,
        }

        if caption:
            data["caption"] = caption

        logger.info(f"Enviando mídia para {phone_number} via {instance_name}")
        return await self._request("POST", f"/message/sendMedia/{instance_name}", data)

    async def get_messages(
        self,
        instance_name: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Obtém mensagens recebidas.

        Args:
            instance_name: Nome da instância.
            limit: Limite de mensagens.

        Returns:
            Lista de mensagens.
        """
        return await self._request(
            "GET",
            f"/message/getHistory/{instance_name}",
            params={"limit": limit},
            data={}
        )

    # ========================================
    # Webhook Setup
    # ========================================

    async def set_webhook(
        self,
        instance_name: str,
        webhook_url: str,
        events: List[str],
        webhook_by_events: bool = False,
    ) -> Dict[str, Any]:
        """
        Configura webhook para receber eventos.

        Args:
            instance_name: Nome da instância.
            webhook_url: URL do webhook.
            events: Lista de eventos (messages, status, etc).
            webhook_by_events: Se True, separa webhooks por evento.

        Returns:
            Confirmação da configuração.
        """
        data = {
            "webhook": {
                "enabled": True,
                "url": webhook_url,
                "webhook_by_events": webhook_by_events,
                "events": events,
            }
        }

        logger.info(f"Configurando webhook para {instance_name}: {webhook_url}")
        return await self._request("POST", f"/webhook/set/{instance_name}", data)

    async def get_webhook(self, instance_name: str) -> Dict[str, Any]:
        """Obtém configuração de webhook."""
        return await self._request("GET", f"/webhook/find/{instance_name}")

    # ========================================
    # Utilities
    # ========================================

    async def logout(self, instance_name: str) -> Dict[str, Any]:
        """
        Desconecta a instância (logout).

        Args:
            instance_name: Nome da instância.

        Returns:
            Confirmação do logout.
        """
        logger.info(f"Fazendo logout da instância: {instance_name}")
        return await self._request("DELETE", f"/instance/logout/{instance_name}")

    def format_phone_number(self, phone: str) -> str:
        """
        Formata número de telefone para WhatsApp.

        Args:
            phone: Número em vários formatos.

        Returns:
            Número formatado (DDI+DDD+NUM, sem + ou símbolos).
        """
        # Remove tudo que não é dígito
        clean = "".join(filter(str.isdigit, phone))

        # Se começar com 0 (Brasil), remove
        if clean.startswith("0"):
            clean = clean[1:]

        # Se não tem DDI Brasil (55), adiciona
        if len(clean) == 11:  # DDD + número Brasil
            clean = "55" + clean

        return clean


# Instância singleton
_whatsapp_service: Optional[EvolutionWhatsAppService] = None


def get_whatsapp_service() -> EvolutionWhatsAppService:
    """Retorna instância do serviço WhatsApp."""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = EvolutionWhatsAppService()
    return _whatsapp_service
