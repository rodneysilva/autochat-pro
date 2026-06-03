"""
Configuração global de testes.

Fixture para app de teste sem dependência de MongoDB/Redis reais.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient

from src.main import criar_aplicacao


@pytest.fixture
def app():
    """App FastAPI de teste (sem lifespan — sem conectar BD real)."""
    app = criar_aplicacao()
    # Sem lifespan para testes unitários
    return app


@pytest.fixture
def mock_mongodb():
    """Mock do MongoDB."""
    mock_db = MagicMock()
    mock_db.users = MagicMock()
    mock_db.bots = MagicMock()
    mock_db.conversations = MagicMock()
    mock_db.automation_rules = MagicMock()
    mock_db.contacts = MagicMock()
    return mock_db


@pytest.fixture
def mock_user_data():
    """Dados de usuário de teste."""
    return {
        "email": "test@example.com",
        "password": "Test@123",
        "name": "Test User",
    }
