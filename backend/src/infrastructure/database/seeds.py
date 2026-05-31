"""
Seeds de dados iniciais.

Cria os planos e configurações padrão do sistema.
"""

from datetime import datetime, timedelta
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


# Configurações dos planos
PLANS_CONFIG = {
    "free": {
        "max_bots": 1,
        "max_messages_per_month": 100,
        "max_contacts": 50,
        "max_automation_rules": 3,
        "max_conversations": 20,
        "features": [
            "1 bot WhatsApp",
            "100 mensagens/mês",
            "Automações básicas",
            "Dashboard básico",
        ]
    },
    "basic": {
        "max_bots": 3,
        "max_messages_per_month": 2000,
        "max_contacts": 500,
        "max_automation_rules": 20,
        "max_conversations": 200,
        "features": [
            "3 bots (WhatsApp + Telegram)",
            "2.000 mensagens/mês",
            "Automações avançadas",
            "Integração LLM",
            "Analytics básico",
            "Suporte email",
        ]
    },
    "pro": {
        "max_bots": 10,
        "max_messages_per_month": 10000,
        "max_contacts": 5000,
        "max_automation_rules": -1,  # ilimitado
        "max_conversations": -1,  # ilimitado
        "features": [
            "10 bots ilimitados",
            "10.000 mensagens/mês",
            "Automações ilimitadas",
            "LLM avançado",
            "Analytics completo",
            "API completa",
            "Suporte prioritário",
            "Whitelabel",
        ]
    }
}


TRIAL_DAYS = 14


async def seed_plans(database: AsyncIOMotorDatabase) -> None:
    """
    Cria as configurações de planos no banco de dados.

    Args:
        database: Instância do banco de dados MongoDB.
    """
    plans_collection = database.plans_config

    # Verificar se já existe
    existing = await plans_collection.count_documents({})
    if existing > 0:
        logger.info("Planos já configurados, pulando seed...")
        return

    # Inserir planos
    plans_to_insert = []

    for plan_type, config in PLANS_CONFIG.items():
        plan_doc = {
            "_id": plan_type,
            "type": plan_type,
            "max_bots": config["max_bots"],
            "max_messages_per_month": config["max_messages_per_month"],
            "max_contacts": config["max_contacts"],
            "max_automation_rules": config["max_automation_rules"],
            "max_conversations": config["max_conversations"],
            "features": config["features"],
            "trial_days": TRIAL_DAYS,
            "created_at": datetime.utcnow(),
        }
        plans_to_insert.append(plan_doc)

    if plans_to_insert:
        await plans_collection.insert_many(plans_to_insert)
        logger.info(f"{len(plans_to_insert)} planos criados com sucesso")


async def seed_system_settings(database: AsyncIOMotorDatabase) -> None:
    """
    Cria as configurações do sistema.

    Args:
        database: Instância do banco de dados MongoDB.
    """
    settings_collection = database.system_settings

    # Verificar se já existe
    existing = await settings_collection.count_documents({})
    if existing > 0:
        logger.info("Configurações do sistema já existem, pulando seed...")
        return

    settings_doc = {
        "_id": "system",
        "maintenance_mode": False,
        "registration_enabled": True,
        "trial_enabled": True,
        "trial_days": TRIAL_DAYS,
        "default_plan": "free",
        "whatsapp_enabled": True,
        "telegram_enabled": True,
        "llm_enabled": True,
        "version": "1.0.0",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    await settings_collection.insert_one(settings_doc)
    logger.info("Configurações do sistema criadas com sucesso")


async def seed_all(database: AsyncIOMotorDatabase) -> None:
    """
    Executa todos os seeds.

    Args:
        database: Instância do banco de dados MongoDB.
    """
    logger.info("=== Iniciando seeds do banco de dados ===")

    await seed_plans(database)
    await seed_system_settings(database)

    logger.info("=== Seeds concluídos ===")


async def run_seed_if_empty(database: AsyncIOMotorDatabase) -> None:
    """
    Executa seeds apenas se o banco estiver vazio.

    Útil para desenvolvimento e testes.

    Args:
        database: Instância do banco de dados MongoDB.
    """
    # Verificar se há usuários (indica banco já em uso)
    users_count = await database.users.count_documents({})

    if users_count == 0:
        logger.info("Banco de dados vazio, executando seeds...")
        await seed_all(database)
    else:
        logger.info("Banco de dados já contém dados, pulando seeds...")
