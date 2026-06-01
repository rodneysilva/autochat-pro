"""
Endpoints da API v1.
"""

from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.whatsapp import router as whatsapp_router
from src.api.v1.endpoints.bots import router as bots_router
from src.api.v1.endpoints.dashboard import router as dashboard_router

__all__ = ["auth_router", "whatsapp_router", "bots_router", "dashboard_router"]
