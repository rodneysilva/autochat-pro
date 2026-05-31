"""
Endpoints da API v1.
"""

from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.whatsapp import router as whatsapp_router

__all__ = ["auth_router", "whatsapp_router"]
