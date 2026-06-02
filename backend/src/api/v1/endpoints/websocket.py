"""
WebSocket em tempo real.

Gerencia conexões WebSocket por user_id, autenticação via JWT,
e broadcast de eventos (mensagens, conversas, métricas).
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from src.application.services.jwt_service import JWTService
from src.shared.exceptions import InvalidTokenException, TokenExpiredException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """Gerencia conexões WebSocket por user_id."""

    def __init__(self):
        # user_id -> lista de conexões ativas
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # user_id -> canais subscritos
        self.subscriptions: Dict[str, Set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        """Registra uma nova conexão WebSocket."""
        await websocket.accept()
        async with self._lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
                self.subscriptions[user_id] = {"messages", "conversations", "metrics"}
            self.active_connections[user_id].append(websocket)
        logger.info(f"WS: usuário {user_id} conectado ({self._count(user_id)} conexões)")

    async def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        """Remove uma conexão WebSocket."""
        async with self._lock:
            if user_id in self.active_connections:
                if websocket in self.active_connections[user_id]:
                    self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    self.subscriptions.pop(user_id, None)
        logger.info(f"WS: usuário {user_id} desconectado ({self._count(user_id)} restantes)")

    async def broadcast_to_user(self, user_id: str, event: dict) -> int:
        """Envia evento para todas as conexões de um usuário."""
        sent = 0
        connections = self.active_connections.get(user_id, [])
        data = json.dumps(event, default=str)
        for ws in connections[:]:
            try:
                await ws.send_text(data)
                sent += 1
            except Exception as e:
                logger.debug(f"WS: erro ao enviar para {user_id}: {e}")
        return sent

    async def broadcast_all(self, event: dict) -> int:
        """Broadcast para todos os usuários conectados (admin)."""
        sent = 0
        data = json.dumps(event, default=str)
        for user_id, connections in list(self.active_connections.items()):
            for ws in connections[:]:
                try:
                    await ws.send_text(data)
                    sent += 1
                except Exception as e:
                    logger.debug(f"WS: erro ao enviar para {user_id}: {e}")
        return sent

    def subscribe(self, user_id: str, channels: List[str]) -> None:
        """Adiciona canais de subscrição para um usuário."""
        if user_id in self.subscriptions:
            self.subscriptions[user_id].update(channels)

    def _count(self, user_id: str) -> int:
        return len(self.active_connections.get(user_id, []))

    def get_stats(self) -> dict:
        """Retorna estatísticas de conexões."""
        total = sum(len(conns) for conns in self.active_connections.values())
        return {
            "usuarios_conectados": len(self.active_connections),
            "total_conexoes": total,
        }


# Singleton global
ws_manager = ConnectionManager()


def get_ws_manager() -> ConnectionManager:
    """Retorna o ConnectionManager global."""
    return ws_manager


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    Endpoint WebSocket principal.

    Autenticação via query param: /ws?token=JWT
    Heartbeat ping/pong a cada 30s.
    Aceita comandos de subscribe via JSON.
    """
    # Validar token
    if not token:
        await websocket.close(code=4001, reason="Token não fornecido")
        return

    try:
        payload = JWTService.decode_token(token)
        if payload.get("type") != "access":
            await websocket.close(code=4003, reason="Tipo de token inválido")
            return

        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4003, reason="Token inválido")
            return
    except (TokenExpiredException, InvalidTokenException):
        await websocket.close(code=4003, reason="Token expirado ou inválido")
        return
    except Exception:
        await websocket.close(code=4003, reason="Erro ao validar token")
        return

    # Conectar
    await ws_manager.connect(user_id, websocket)

    # Enviar confirmação
    try:
        await websocket.send_text(json.dumps({
            "event": "connected",
            "data": {
                "user_id": user_id,
                "channels": list(ws_manager.subscriptions.get(user_id, set())),
            }
        }))
    except Exception:
        await ws_manager.disconnect(user_id, websocket)
        return

    # Loop principal: receber mensagens e heartbeat
    try:
        while True:
            # Wait com timeout para heartbeat
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                await _handle_message(user_id, message)
            except asyncio.TimeoutError:
                # Heartbeat ping
                try:
                    await websocket.send_text(json.dumps({"event": "ping"}))
                except Exception:
                    break
    except WebSocketDisconnect:
        logger.debug(f"WS: WebSocketDisconnect para {user_id}")
    except Exception as e:
        logger.debug(f"WS: erro no loop para {user_id}: {e}")
    finally:
        await ws_manager.disconnect(user_id, websocket)


async def _handle_message(user_id: str, raw: str) -> None:
    """Processa mensagens recebidas do cliente."""
    try:
        data = json.loads(raw)
        action = data.get("action")

        if action == "subscribe":
            channels = data.get("channels", [])
            if isinstance(channels, list) and channels:
                ws_manager.subscribe(user_id, channels)
                # Confirmar subscrição
                connections = ws_manager.active_connections.get(user_id, [])
                for ws in connections:
                    try:
                        await ws.send_text(json.dumps({
                            "event": "subscribed",
                            "data": {"channels": channels}
                        }))
                    except Exception:
                        pass
                logger.debug(f"WS: {user_id} subscreveu em {channels}")

        elif action == "pong":
            pass  # Resposta do heartbeat, ignora

    except json.JSONDecodeError:
        pass  # Mensagem inválida, ignora
    except Exception as e:
        logger.debug(f"WS: erro ao processar mensagem de {user_id}: {e}")
