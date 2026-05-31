"""
Serviços de WhatsApp para verificação.
"""

from .whatsapp_service import (
    WhatsAppVerificationService,
    get_whatsapp_service,
)

__all__ = [
    "WhatsAppVerificationService",
    "get_whatsapp_service",
]
