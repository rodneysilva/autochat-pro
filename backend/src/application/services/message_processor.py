"""
Processador de mensagens WhatsApp.

Recebe mensagens do webhook da Evolution API, busca config do bot,
verifica horário e gera resposta com IA GLM ou mensagem padrão.
"""

import asyncio
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4 as _uuid4

from src.infrastructure.external_services.whatsapp.evolution_service import EvolutionWhatsAppService
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class MessageProcessor:
    """Processa mensagens recebidas via webhook e gera respostas."""

    def __init__(self, bot_repository, automation_rule_repository=None, evolution_service: EvolutionWhatsAppService = None):
        self._bot_repo = bot_repository
        self._automation_repo = automation_rule_repository
        self._whatsapp = evolution_service
        self._context_service = None
        self._llm_service = None

    def set_context_service(self, context_service):
        """Define o serviço de contexto de conversa."""
        self._context_service = context_service

    def set_llm_service(self, llm_service):
        """Define o serviço LLM unificado."""
        self._llm_service = llm_service

    async def process_incoming_message(self, instance_name: str, event: dict) -> Optional[str]:
        """
        Processa uma mensagem recebida via webhook.

        Args:
            instance_name: Nome da instância Evolution API.
            event: Payload do webhook.

        Returns:
            ID da mensagem enviada como resposta, ou None se não houver resposta.
        """
        try:
            # Extrair dados da mensagem
            message_data = self._extract_message(event)
            if not message_data:
                logger.warning(f"Mensagem ignorada para {instance_name}: dados inválidos")
                return None

            phone_number = message_data["from"]
            message_text = message_data["text"]
            message_id = message_data["id"]
            push_name = message_data.get("push_name", "Cliente")

            logger.info(
                f"Mensagem recebida: {instance_name} | de: {phone_number} | "
                f"texto: {message_text[:50]}..."
            )

            # Buscar bot pelo instance_name
            bot = await self._bot_repo.buscar_por_nome_instancia(instance_name)
            if not bot:
                logger.warning(f"Bot não encontrado para instância: {instance_name}")
                return None

            # Verificar se bot está ativo
            if bot.status.value != "active":
                logger.info(f"Bot {bot.nome} está inativo (status={bot.status.value}), ignorando mensagem")
                return None

            # Verificar horário de funcionamento
            if bot.working_hours.ativado:
                if not self._is_within_working_hours(bot.working_hours):
                    # Enviar mensagem de fora de horário
                    if bot.working_hours.mensagem_fora_horario:
                        # Personalizar com nome se disponível
                        msg = bot.working_hours.mensagem_fora_horario.replace(
                            "{nome}", push_name
                        )
                        response_id = await self._whatsapp.send_text(
                            instance_name, phone_number, msg
                        )
                        logger.info(
                            f"Mensagem fora de horário enviada para {phone_number}"
                        )
                        return response_id
                    return None

            # ---- Automações: avaliar regras ANTES de LLM ----
            automation_response = await self._try_automation_rules(
                bot, message_text, push_name, phone_number, instance_name
            )
            if automation_response is not None:
                return automation_response

            # Fallback: gerar resposta via LLM ou padrão
            if bot.llm_config.ativado:
                response_text = await self._generate_llm_response(
                    bot, message_text, push_name, phone_number
                )
            elif bot.mensagem_resposta_padrao:
                response_text = bot.mensagem_resposta_padrao.replace(
                    "{nome}", push_name
                )
            else:
                logger.info(f"Sem resposta configurada para bot {bot.nome}")
                return None

            if not response_text:
                return None

            # Enviar resposta (com retry e error handling)
            try:
                response_id = await self._whatsapp.send_text(
                    instance_name, phone_number, response_text
                )
            except Exception as e:
                logger.error(f"Erro ao enviar resposta para {phone_number}: {e}")
                return None

            # Atualizar estatísticas do bot
            await self._update_bot_stats(bot)

            # Emitir eventos WebSocket em tempo real
            await self._emit_ws_events(bot, phone_number, message_text, response_id, push_name)

            logger.info(
                f"Resposta enviada para {phone_number} via bot {bot.nome}"
            )
            return response_id

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            return None

    async def _try_automation_rules(
        self, bot, message_text: str, push_name: str,
        phone_number: str, instance_name: str,
    ) -> Optional[str]:
        """
        Tenta aplicar regras de automação antes de ir para o LLM.
        Retorna o response_id se uma regra bateu e executou, ou None se deve fallback.
        """
        if not self._automation_repo:
            return None

        try:
            from src.domain.entities.automation_rule import (
                TipoAcao, RegraAutomacao,
            )

            rules = await self._automation_repo.buscar_ativas_por_bot(bot.id)
            if not rules:
                return None

            # Ordenar por prioridade (maior primeiro)
            rules.sort(key=lambda r: r.prioridade, reverse=True)

            # Contexto para avaliação
            contexto = {
                "message.content": message_text,
                "customer.name": push_name,
                "message.type": "text",
            }

            # Gerar um conversation_id simples para cooldown
            conv_id = _uuid4()

            for rule in rules:
                if not rule.pode_executar(conv_id):
                    continue

                if not rule.avaliar_condicoes(contexto):
                    continue

                # Regra bateu! Executar ações
                logger.info(
                    f"Regra de automação '{rule.nome}' acionada para {phone_number}"
                )
                rule.executar(conv_id)

                # Processar ações ordenadas por delay
                response_id = None
                for delay, acao in rule.obter_acoes_com_delay():
                    if delay > 0:
                        logger.info(f"Aguardando {delay}s (delay da ação)...")
                        await asyncio.sleep(delay)

                    if acao.tipo == TipoAcao.RESPONDER:
                        msg = acao.conteudo.replace("{nome}", push_name)
                        msg = msg.replace("{telefone}", phone_number)
                        response_id = await self._whatsapp.send_text(
                            instance_name, phone_number, msg
                        )

                    elif acao.tipo == TipoAcao.USAR_LLM:
                        response_text = await self._generate_llm_response(
                            bot, message_text, push_name, phone_number
                        )
                        if response_text:
                            response_id = await self._whatsapp.send_text(
                                instance_name, phone_number, response_text
                            )

                    elif acao.tipo == TipoAcao.ENCAMINHAR:
                        dest = acao.parametros.get("destino", "")
                        if dest:
                            msg = acao.conteudo or message_text
                            try:
                                await self._whatsapp.send_text(
                                    instance_name, dest, msg
                                )
                            except Exception as e:
                                logger.error(f"Erro ao encaminhar mensagem: {e}")

                    elif acao.tipo == TipoAcao.FECHAR_CONVERSA:
                        logger.info(f"Ação close executada para conversa de {phone_number}")

                    elif acao.tipo == TipoAcao.ATRIBUIR_HUMANO:
                        logger.info(f"Ação assign_human executada para conversa de {phone_number}")

                    elif acao.tipo == TipoAcao.ADICIONAR_TAG:
                        tag = acao.conteudo
                        logger.info(f"Ação tag executada: tag={tag} para {phone_number}")

                # Atualizar estatísticas do bot
                await self._update_bot_stats(bot)

                if response_id:
                    logger.info(f"Resposta de automação enviada para {phone_number}")

                # Emitir eventos WebSocket em tempo real
                await self._emit_ws_events(bot, phone_number, message_text, response_id, push_name)

                return response_id

            return None

        except Exception as e:
            logger.error(f"Erro ao avaliar automações: {e}", exc_info=True)
            return None

    async def _emit_ws_events(
        self, bot, phone_number: str, message_text: str,
        response_id: Optional[str], push_name: str,
    ) -> None:
        """Emite eventos WebSocket após processar mensagem."""
        try:
            from src.api.v1.endpoints.websocket import get_ws_manager
            manager = get_ws_manager()

            bot_owner_id = getattr(bot, 'usuario_id', None) or str(bot.usuario_id) if hasattr(bot, 'usuario_id') else None
            if not bot_owner_id:
                return

            # Evento: nova mensagem
            await manager.broadcast_to_user(bot_owner_id, {
                "event": "message.new",
                "data": {
                    "bot_id": str(bot.id),
                    "bot_name": getattr(bot, 'nome', ''),
                    "phone_number": phone_number,
                    "message_text": message_text[:100],
                    "push_name": push_name,
                    "response_id": response_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            })

            # Evento: atualizar métricas
            await manager.broadcast_to_user(bot_owner_id, {
                "event": "metrics.updated",
                "data": {}
            })

        except Exception as e:
            logger.debug(f"WS: erro ao emitir eventos: {e}")

    def _extract_message(self, event: dict) -> Optional[dict]:
        """
        Extrai dados da mensagem do evento do webhook.

        Formato Evolution API v2:
        {
            "event": "messages.upsert",
            "data": {
                "key": {"remoteJid": "55119...", "id": "..."},
                "message": {"conversation": "texto da msg"},
                "pushName": "João",
                ...
            }
        }
        """
        try:
            event_type = event.get("event", "")

            # Só processar mensagens novas (Evolution API v2 usa MESSAGES_UPSERT)
            if event_type not in ("messages.upsert", "MESSAGES_UPSERT"):
                return None

            data = event.get("data", {})

            # Verificar se é mensagem recebida (não enviada pelo bot)
            # Mensagens recebidas vêm de "s.whatsapp.net" ou com "fromMe": false
            key = data.get("key", {})
            from_me = key.get("fromMe", False)
            if from_me:
                return None

            # Extrair número do remetente
            remote_jid = key.get("remoteJid", "")
            if not remote_jid:
                return None

            # Ignorar mensagens de grupo (só responder conversas diretas)
            if "@g.us" in remote_jid:
                return None

            # Ignorar se não for pessoa física
            if "@s.whatsapp.net" not in remote_jid:
                return None

            # Remover @s.whatsapp.net para obter apenas o número
            phone_number = remote_jid.split("@")[0]

            # Extrair texto da mensagem
            message = data.get("message", {})
            text = (
                message.get("conversation", "")
                or message.get("extendedTextMessage", {}).get("text", "")
                or ""
            )

            if not text:
                # Mensagem sem texto (imagem, áudio, etc) - ignorar por enquanto
                return None

            return {
                "from": phone_number,
                "text": text,
                "id": key.get("id", ""),
                "push_name": data.get("pushName", "Cliente"),
            }
        except Exception as e:
            logger.error(f"Erro ao extrair mensagem do evento: {e}")
            return None

    async def _generate_llm_response(
        self, bot, message_text: str, sender_name: str, phone_number: str = ""
    ) -> Optional[str]:
        """Gera resposta usando LLM (multi-provider com contexto de conversa)."""
        try:
            from src.infrastructure.external_services.llm.llm_service import (
                LLMProvider, get_llm_service, DEFAULT_MODELS,
            )
            from src.application.services.conversation_context import get_context_service

            llm = self._llm_service or get_llm_service()
            ctx_svc = self._context_service or get_context_service()

            # Determinar provider e modelo
            provider_name = getattr(bot.llm_config, 'provider', 'glm') or 'glm'
            try:
                provider = LLMProvider(provider_name)
            except ValueError:
                provider = LLMProvider.GLM

            model = bot.llm_config.modelo or DEFAULT_MODELS.get(provider, "glm-4")

            # Construir system prompt personalizado
            system_prompt = bot.llm_config.system_prompt
            if ctx_svc and system_prompt:
                system_prompt = ctx_svc.build_system_prompt(
                    base_prompt=system_prompt,
                    bot_name=bot.nome,
                )
                if sender_name and sender_name != "Cliente":
                    system_prompt += f"\n\nO cliente se chama {sender_name}."

            # Buscar contexto de conversa se disponível
            context_messages = []
            max_ctx = getattr(bot.llm_config, 'max_context_messages', 20) or 20

            if ctx_svc and phone_number:
                try:
                    from src.infrastructure.database.mongodb import MongoDB
                    db = MongoDB.get_database()
                    from bson import ObjectId
                    conversations = await db.conversations.find(
                        {
                            "bot_id": ObjectId(str(bot.id)),
                            "customer.id": phone_number,
                            "status": {"$in": ["active", "waiting"]},
                        }
                    ).sort("updated_at", -1).limit(1).to_list(1)

                    if conversations:
                        conv_id = str(conversations[0]["_id"])
                        context_messages = await ctx_svc.get_context_messages(
                            conversation_id=conv_id,
                            bot_system_prompt="",
                            max_tokens=3000,
                            max_messages=max_ctx,
                        )
                        logger.info(f"Contexto: {len(context_messages)} mensagens de histórico")
                except Exception as e:
                    logger.debug(f"Sem contexto de conversa: {e}")

            # Adicionar mensagem atual do usuário
            context_messages.append({"role": "user", "content": message_text})

            # Chamar LLM unificado
            response = await llm.chat(
                provider=provider,
                model=model,
                messages=context_messages,
                system_prompt=system_prompt or None,
                temperature=bot.llm_config.temperatura or 0.7,
                max_tokens=bot.llm_config.max_tokens or 2048,
            )

            return response.strip()

        except Exception as e:
            logger.error(f"Erro ao gerar resposta LLM: {e}")
            # Fallback: tentar GLM legado
            try:
                from src.infrastructure.external_services.llm.glm_service import get_glm_service
                glm = get_glm_service()
                sp = bot.llm_config.system_prompt or "Você é um assistente de atendimento ao cliente amigável e profissional."
                if sender_name and sender_name != "Cliente":
                    sp = f"Contexto: O cliente se chama {sender_name}.\n\n{sp}"
                response = await glm.generate_response(
                    user_message=message_text,
                    system_prompt=sp,
                    model=bot.llm_config.modelo,
                    temperature=bot.llm_config.temperatura,
                    max_tokens=bot.llm_config.max_tokens,
                )
                return response.strip()
            except Exception as fallback_err:
                logger.error(f"Fallback GLM também falhou: {fallback_err}")
            if bot.mensagem_resposta_padrao:
                return bot.mensagem_resposta_padrao
            return None

    def _is_within_working_hours(self, working_hours) -> bool:
        """Verifica se o horário atual está dentro do horário de funcionamento."""
        try:
            now = datetime.now()

            # Parsing simples dos horários (HH:MM)
            try:
                hora_inicio = int(working_hours.inicio.split(":")[0])
                min_inicio = int(working_hours.inicio.split(":")[1])
                hora_fim = int(working_hours.fim.split(":")[0])
                min_fim = int(working_hours.fim.split(":")[1])
            except (ValueError, IndexError):
                logger.error(f"Formato de horário inválido: {working_hours.inicio} - {working_hours.fim}")
                return True  # Se horário inválido, assume dentro do horário

            current_minutes = now.hour * 60 + now.minute
            start_minutes = hora_inicio * 60 + min_inicio
            end_minutes = hora_fim * 60 + min_fim

            # Verificar dia da semana (0=seg, 6=dom)
            # Por padrão, todos os dias
            if start_minutes <= end_minutes:
                return start_minutes <= current_minutes <= end_minutes
            else:
                # Horário cruza meia-noite (ex: 22:00 - 06:00)
                return current_minutes >= start_minutes or current_minutes <= end_minutes

        except Exception as e:
            logger.error(f"Erro ao verificar horário: {e}")
            return True

    async def process_telegram_message(self, bot_token: str, update_data: dict) -> Optional[str]:
        """
        Processa uma mensagem recebida via webhook do Telegram.

        Args:
            bot_token: Token do bot Telegram.
            update_data: Payload do update do Telegram.

        Returns:
            ID da resposta enviada, ou None.
        """
        try:
            message = update_data.get("message") or update_data.get("edited_message")
            if not message:
                return None

            chat = message.get("chat", {})
            chat_id = str(chat.get("id", ""))
            message_text = message.get("text", "")

            if not message_text:
                logger.debug(f"Mensagem Telegram sem texto, ignorando (chat_id={chat_id})")
                return None

            # Ignorar mensagens do próprio bot
            from_user = message.get("from", {})
            if from_user.get("is_bot", False):
                return None

            sender_name = from_user.get("first_name", "Cliente") or "Cliente"
            message_id = message.get("message_id", "")

            logger.info(
                f"Mensagem Telegram recebida: chat_id={chat_id} | de: {sender_name} | "
                f"texto: {message_text[:50]}..."
            )

            # Buscar bot pelo token
            bot_doc = None
            from src.infrastructure.database.mongodb import MongoDB
            db = MongoDB.get_database()
            bot_doc = await db.bots.find_one({"telegram_config.bot_token": bot_token})
            if not bot_doc:
                logger.warning(f"Bot não encontrado para token Telegram=...{bot_token[-6:]}")
                return None

            # Reconstruir entidade Bot a partir do documento
            from src.infrastructure.repositories.bot_repository_impl import MongoBotRepository
            bot_repo_instance = type(self._bot_repo)(db)
            bot = await bot_repo_instance.buscar_por_id(str(bot_doc["_id"]))
            if not bot:
                return None

            if bot.status.value != "active":
                logger.info(f"Bot Telegram {bot.nome} está inativo, ignorando mensagem")
                return None

            # Verificar horário de funcionamento
            if bot.working_hours.ativado:
                if not self._is_within_working_hours(bot.working_hours):
                    if bot.working_hours.mensagem_fora_horario:
                        msg = bot.working_hours.mensagem_fora_horario.replace("{nome}", sender_name)
                        await self._send_telegram_response(bot_token, chat_id, msg)
                        return "off_hours"
                    return None

            # Automações
            automation_response = await self._try_telegram_automation_rules(
                bot, message_text, sender_name, chat_id, bot_token
            )
            if automation_response is not None:
                return automation_response

            # LLM ou mensagem padrão
            if bot.llm_config.ativado:
                response_text = await self._generate_llm_response(
                    bot, message_text, sender_name, chat_id
                )
            elif bot.mensagem_resposta_padrao:
                response_text = bot.mensagem_resposta_padrao.replace("{nome}", sender_name)
            else:
                logger.info(f"Sem resposta configurada para bot Telegram {bot.nome}")
                return None

            if not response_text:
                return None

            await self._send_telegram_response(bot_token, chat_id, response_text)
            await self._update_bot_stats(bot)

            # Salvar conversa e mensagem no MongoDB
            try:
                from src.infrastructure.database.mongodb import MongoDB
                from datetime import datetime, timezone
                db = MongoDB.get_database()
                now = datetime.now(timezone.utc)
                # Buscar ou criar conversa
                conv = await db.conversations.find_one({"bot_id": str(bot.id), "customer_phone": chat_id})
                if not conv:
                    conv_result = await db.conversations.insert_one({
                        "bot_id": str(bot.id),
                        "customer_phone": chat_id,
                        "customer_name": sender_name,
                        "customer_platform": "telegram",
                        "status": "active",
                        "criado_em": now,
                        "atualizado_em": now,
                    })
                    conv_id = str(conv_result.inserted_id)
                else:
                    conv_id = str(conv["_id"])
                    await db.conversations.update_one({"_id": conv["_id"]}, {"$set": {"atualizado_em": now}})
                # Salvar mensagem do cliente
                await db.messages.insert_one({
                    "conversation_id": conv_id,
                    "bot_id": str(bot.id),
                    "sender": "customer",
                    "content": message_text,
                    "timestamp": now,
                })
                # Salvar resposta do bot
                await db.messages.insert_one({
                    "conversation_id": conv_id,
                    "bot_id": str(bot.id),
                    "sender": "bot",
                    "content": response_text,
                    "timestamp": now,
                })
            except Exception as save_err:
                logger.warning(f"Erro ao salvar conversa Telegram (não crítico): {save_err}")

            # WS events
            await self._emit_ws_events(bot, chat_id, message_text, "sent", sender_name)

            logger.info(f"Resposta Telegram enviada para chat_id={chat_id} via bot {bot.nome}")
            return "sent"

        except Exception as e:
            logger.error(f"Erro ao processar mensagem Telegram: {e}", exc_info=True)
            return None

    async def _send_telegram_response(self, bot_token: str, chat_id: str, text: str) -> None:
        """Envia resposta via TelegramService."""
        from src.infrastructure.external_services.telegram import get_telegram_service
        telegram_svc = get_telegram_service()
        # Telegram markdown pode quebrar com caracteres especiais; usar HTML seguro
        safe_text = text.replace("<", "&lt;").replace(">", "&gt;")
        safe_text = safe_text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
        safe_text = safe_text.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
        safe_text = safe_text.replace("&lt;code&gt;", "<code>").replace("&lt;/code&gt;", "</code>")
        await telegram_svc.send_message(bot_token, chat_id, safe_text, parse_mode="HTML")

    async def _try_telegram_automation_rules(
        self, bot, message_text: str, sender_name: str,
        chat_id: str, bot_token: str,
    ) -> Optional[str]:
        """Avalia automações para mensagens Telegram."""
        if not self._automation_repo:
            return None

        try:
            from src.domain.entities.automation_rule import TipoAcao

            rules = await self._automation_repo.buscar_ativas_por_bot(bot.id)
            if not rules:
                return None

            rules.sort(key=lambda r: r.prioridade, reverse=True)
            contexto = {
                "message.content": message_text,
                "customer.name": sender_name,
                "message.type": "text",
            }
            conv_id = _uuid4()

            for rule in rules:
                if not rule.pode_executar(conv_id):
                    continue
                if not rule.avaliar_condicoes(contexto):
                    continue

                logger.info(f"Regra de automação '{rule.nome}' acionada para Telegram chat_id={chat_id}")
                rule.executar(conv_id)

                response_id = None
                for delay, acao in rule.obter_acoes_com_delay():
                    if delay > 0:
                        await asyncio.sleep(delay)

                    if acao.tipo == TipoAcao.RESPONDER:
                        msg = acao.conteudo.replace("{nome}", sender_name)
                        await self._send_telegram_response(bot_token, chat_id, msg)
                        response_id = "sent"

                    elif acao.tipo == TipoAcao.USAR_LLM:
                        response_text = await self._generate_llm_response(
                            bot, message_text, sender_name, chat_id
                        )
                        if response_text:
                            await self._send_telegram_response(bot_token, chat_id, response_text)
                            response_id = "sent"

                    elif acao.tipo == TipoAcao.FECHAR_CONVERSA:
                        logger.info(f"Ação close para Telegram chat_id={chat_id}")

                    elif acao.tipo == TipoAcao.ATRIBUIR_HUMANO:
                        logger.info(f"Ação assign_human para Telegram chat_id={chat_id}")

                    elif acao.tipo == TipoAcao.ADICIONAR_TAG:
                        logger.info(f"Ação tag para Telegram chat_id={chat_id}: {acao.conteudo}")

                await self._update_bot_stats(bot)
                await self._emit_ws_events(bot, chat_id, message_text, response_id, sender_name)
                return response_id

            return None

        except Exception as e:
            logger.error(f"Erro ao avaliar automações Telegram: {e}", exc_info=True)
            return None

    async def _update_bot_stats(self, bot) -> None:
        """Atualiza estatísticas do bot."""
        try:
            bot.estatisticas.total_mensagens += 1
            await self._bot_repo.salvar(bot)
        except Exception as e:
            logger.error(f"Erro ao atualizar estatísticas: {e}")


# Instância global (inicializada no startup do app)
_processor: Optional[MessageProcessor] = None


def get_message_processor() -> Optional[MessageProcessor]:
    """Retorna instância global do MessageProcessor."""
    return _processor


def init_message_processor(bot_repository, automation_rule_repository=None, evolution_service=None) -> MessageProcessor:
    """Inicializa o MessageProcessor global."""
    global _processor
    _processor = MessageProcessor(bot_repository, automation_rule_repository, evolution_service)
    return _processor
