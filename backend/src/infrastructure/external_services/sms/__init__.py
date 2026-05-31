"""
Serviço de SMS.
"""

from src.infrastructure.external_services.sms.sms_service import (
    SMSService,
    get_sms_service,
)

__all__ = ["SMSService", "get_sms_service"]
