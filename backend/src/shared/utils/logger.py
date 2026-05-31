"""
Configuração de logging.

Módulo central para configuração de logging da aplicação.
"""

import logging
import sys
from typing import Optional


def configurar_logger(
    level: str = "INFO",
    formato: Optional[str] = None,
) -> None:
    """
    Configura o logger global da aplicação.

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        formato: Formato personalizado das mensagens de log
    """
    if formato is None:
        formato = (
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    # Configurar root logger
    logging.basicConfig(
        level=level,
        format=formato,
        stream=sys.stdout,
        force=True,  # Força reconfiguração mesmo que já tenha sido configurado
    )

    # Reduzir verbosidade de bibliotecas externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(nome: str) -> logging.Logger:
    """
    Retorna um logger com o nome especificado.

    Args:
        nome: Nome do logger

    Returns:
        Instância de Logger
    """
    return logging.getLogger(nome)
