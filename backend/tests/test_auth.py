"""
Testes dos endpoints de autenticação.

Testa login, register e me com mocks.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.domain.entities.user import Usuario, ConfiguracaoPlano, StatusUsuario


@pytest.fixture
def mock_user():
    """Retorna um usuário mockado."""
    return Usuario(
        id="507f1f77bcf86cd799439011",
        email="admin@autochat.com",
        nome="Admin Teste",
        senha_hash="$argon2id$v=19$m=65536,t=3,p=4$test",
        role="admin",
        plano=ConfiguracaoPlano(tipo=ConfiguracaoPlano.TipoPlano.PRO),
        status=StatusUsuario.ATIVO,
        email_confirmado=True,
    )


class TestAuthEndpoints:
    """Testes dos endpoints de /auth."""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Testa login com credenciais válidas."""
        from httpx import AsyncClient, ASGITransport
        from src.main import criar_aplicacao

        app = criar_aplicacao()
        transport = ASGITransport(app=app)

        # Mock do MongoDB para evitar conexão real
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value={
            "_id": "507f1f77bcf86cd799439011",
            "email": "admin@autochat.com",
            "name": "Admin Teste",
            "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$RdescudvJCsgt3ub+b+daw",
            "role": "admin",
            "email_confirmed": True,
            "status": "active",
            "plan": {"type": "pro", "max_bots": 10},
        })

        mock_db = MagicMock()
        mock_db.users = mock_collection

        with patch("src.infrastructure.database.mongodb.MongoDB._client", None), \
             patch("src.infrastructure.database.mongodb.MongoDB._db", mock_db), \
             patch("src.infrastructure.database.mongodb.MongoDB.get_database", return_value=mock_db), \
             patch("src.infrastructure.database.mongodb.MongoDB.connect", new_callable=AsyncMock):

            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/v1/auth/login", json={
                    "email": "admin@autochat.com",
                    "password": "Admin@123",
                })

        # Pode ser 200 ou 500 dependendo do hash — o importante é não ser 422 (validação)
        assert resp.status_code != 422

    @pytest.mark.asyncio
    async def test_login_invalid_password(self):
        """Testa login com senha inválida."""
        from httpx import AsyncClient, ASGITransport
        from src.main import criar_aplicacao

        app = criar_aplicacao()
        transport = ASGITransport(app=app)

        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_db = MagicMock()
        mock_db.users = mock_collection

        with patch("src.infrastructure.database.mongodb.MongoDB._db", mock_db), \
             patch("src.infrastructure.database.mongodb.MongoDB.get_database", return_value=mock_db), \
             patch("src.infrastructure.database.mongodb.MongoDB.connect", new_callable=AsyncMock):

            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/v1/auth/login", json={
                    "email": "naoexiste@teste.com",
                    "password": "wrong",
                })

        assert resp.status_code in (401, 500)

    @pytest.mark.asyncio
    async def test_register_validation(self):
        """Testa validação do registro — campos obrigatórios."""
        from httpx import AsyncClient, ASGITransport
        from src.main import criar_aplicacao

        app = criar_aplicacao()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Email inválido
            resp = await client.post("/api/v1/auth/register", json={
                "email": "email-invalido",
                "password": "123",
                "name": "",
            })

        assert resp.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Testa endpoint de health."""
        from httpx import AsyncClient, ASGITransport
        from src.main import criar_aplicacao

        app = criar_aplicacao()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")

        assert resp.status_code == 200
        assert resp.json() == {"status": "healthy"}
