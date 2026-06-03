"""
Aplicação principal AutoChat Pro.

Ponto de entrada da aplicação FastAPI com configuração de middlewares,
rotas e injeção de dependências.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.shared.config import settings
from src.shared.exceptions import (
    BaseAppException,
    BusinessRuleException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
    LimitExceededException,
)
from src.shared.utils.logger import configurar_logger


# Configurar logger
configurar_logger(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Gerencia o ciclo de vida da aplicação.

    Inicializa recursos ao iniciar e limpa ao encerrar.
    """
    logger.info("🚀 Iniciando AutoChat Pro...")
    logger.info(f"Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")

    # Inicializar MongoDB
    from src.infrastructure.database.mongodb import MongoDB

    try:
        await MongoDB.connect()
        logger.info("✅ MongoDB conectado")

        # Criar índices
        from src.infrastructure.database.indexes import create_all_indexes
        await create_all_indexes(MongoDB.get_database())
        logger.info("✅ Índices criados")

        # Executar seeds se necessário
        from src.infrastructure.database.seeds import run_seed_if_empty
        await run_seed_if_empty(MongoDB.get_database())

        # Inicializar MessageProcessor (webhook → IA → resposta)
        try:
            from src.infrastructure.repositories.bot_repository_impl import MongoBotRepository
            from src.infrastructure.repositories.automation_rule_repository_impl import MongoAutomationRuleRepository
            from src.infrastructure.external_services.whatsapp import get_whatsapp_service
            from src.application.services.message_processor import init_message_processor, get_message_processor

            bot_repo = MongoBotRepository(MongoDB.get_database())
            automation_repo = MongoAutomationRuleRepository(MongoDB.get_database())
            whatsapp_svc = get_whatsapp_service()
            init_message_processor(bot_repo, automation_repo, whatsapp_svc)
            logger.info("✅ MessageProcessor inicializado")

            # Inicializar serviços LLM avançados
            try:
                from src.infrastructure.external_services.llm.llm_service import init_llm_service
                from src.application.services.conversation_context import init_context_service

                llm_svc = init_llm_service()
                ctx_svc = init_context_service(MongoDB.get_database())

                processor = get_message_processor()
                if processor:
                    processor.set_llm_service(llm_svc)
                    processor.set_context_service(ctx_svc)
                logger.info("✅ LLM Service e ConversationContext inicializados")
            except Exception as e:
                logger.error(f"⚠️ Erro ao inicializar LLM avançado: {e}")
        except Exception as e:
            logger.error(f"⚠️ Erro ao inicializar MessageProcessor: {e}")

    except Exception as e:
        logger.error(f"❌ Erro ao conectar MongoDB: {e}")





    yield


    logger.info("🛑 Encerrando AutoChat Pro...")

    # Limpeza de recursos
    await MongoDB.disconnect()
    logger.info("✅ MongoDB desconectado")


def criar_aplicacao() -> FastAPI:
    """
    Cria e configura a aplicação FastAPI.

    Returns:
        Aplicação FastAPI configurada
    """
    app = FastAPI(
        title="AutoChat Pro",
        description="Plataforma de automação de atendimento via WhatsApp e Telegram",
        version="1.0.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ========================================
    # CORS
    # ========================================
    if settings.is_development:
        # Em desenvolvimento, permitir qualquer origem
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ========================================
    # Exception Handlers
    # ========================================

    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        """Handler para exceções da aplicação."""
        logger.warning(f"Exceção da aplicação: {exc.code} - {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "erro": {
                    "codigo": exc.code,
                    "mensagem": exc.message,
                    "detalhes": exc.details,
                }
            },
        )

    @app.exception_handler(EntityNotFoundException)
    async def not_found_handler(request: Request, exc: EntityNotFoundException) -> JSONResponse:
        """Handler para entidade não encontrada."""
        logger.info(f"Recurso não encontrado: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "erro": {
                    "codigo": exc.code,
                    "mensagem": exc.message,
                }
            },
        )

    @app.exception_handler(EntityAlreadyExistsException)
    async def conflict_handler(request: Request, exc: EntityAlreadyExistsException) -> JSONResponse:
        """Handler para conflito de entidade."""
        logger.warning(f"Conflito: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "erro": {
                    "codigo": exc.code,
                    "mensagem": exc.message,
                }
            },
        )

    @app.exception_handler(LimitExceededException)
    async def limit_exceeded_handler(request: Request, exc: LimitExceededException) -> JSONResponse:
        """Handler para limite excedido."""
        logger.warning(f"Limite excedido: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "erro": {
                    "codigo": exc.code,
                    "mensagem": exc.message,
                    "detalhes": exc.details,
                }
            },
        )

    @app.exception_handler(BusinessRuleException)
    async def business_rule_handler(request: Request, exc: BusinessRuleException) -> JSONResponse:
        """Handler para violação de regra de negócio."""
        logger.warning(f"Regra de negócio violada: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "erro": {
                    "codigo": exc.code,
                    "mensagem": exc.message,
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handler para exceções genéricas não tratadas."""
        logger.error(f"Exceção não tratada: {type(exc).__name__} - {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "erro": {
                    "codigo": "INTERNAL_ERROR",
                    "mensagem": "Erro interno do servidor" if not settings.is_development else str(exc),
                }
            },
        )

    # ========================================
    # Rotas
    # ========================================

    @app.get("/", tags=["Health"])
    async def raiz():
        """Rota raiz para verificação de saúde."""
        return {
            "servico": "AutoChat Pro",
            "versao": "1.0.0",
            "status": "operacional",
            "ambiente": settings.ENVIRONMENT,
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Endpoint para health check."""
        return {"status": "healthy"}

    # Registro de rotas da API v1
    from src.api.v1.endpoints import auth_router, whatsapp_router, bots_router, dashboard_router, automations_router, chat_router, telegram_router

    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(whatsapp_router, prefix=settings.API_V1_PREFIX)
    app.include_router(bots_router, prefix=settings.API_V1_PREFIX)
    app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
    app.include_router(automations_router, prefix=settings.API_V1_PREFIX)
    app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
    app.include_router(telegram_router, prefix=settings.API_V1_PREFIX)

    return app


# Instância da aplicação
app = criar_aplicacao()



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
