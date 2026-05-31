"""
Serviços de WhatsApp para Evolution API.
"""

from .evolution_service import (
    EvolutionWhatsAppService,
    WhatsAppConnectionStatus,
    get_whatsapp_service,
)

# Mantiver compatibilidade com verificação
from .whatsapp_service import (
    WhatsAppVerificationService,
    get_whatsapp_service as get_verification_service,
)

__all__ = [
    "EvolutionWhatsAppService",
    "WhatsAppConnectionStatus",
    "get_whatsapp_service",
    "WhatsAppVerificationService",
    "get_verification_service",
]
