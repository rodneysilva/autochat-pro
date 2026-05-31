"""
Serviço de email.
"""

from src.infrastructure.external_services.email.email_service import (
    EmailService,
    EmailSchema,
    get_email_service,
)

__all__ = ["EmailService", "EmailSchema", "get_email_service"]
