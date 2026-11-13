"""Botni ishga tushirish: polling (lokal) yoki webhook (hosting)."""
from __future__ import annotations

import logging

from telegram import BotCommand, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, ContextTypes, Defaults, MessageHandler, filters,
)

from app.config import Settings, get_settings
from app.database.connection import close_db, init_db, init_engine
from app.handlers import calculator, converter, currency, reminders, tasks, translate, weather
from app.handlers import help as help_handler
from app.handlers import start as start_handler
from app.handlers.router import cancel, route_text
from app.logging_config import setup_logging
from app.services.scheduler import CHECK_INTERVAL, check_due_reminders

logger = logging.getLogger(__name__)

COMMANDS = [
    BotCommand("start", "Botni ishga tushirish"),
    BotCommand("menu", "Asosiy menyu"),
    BotCommand("bekor", "Joriy amalni bekor qilish"),
    BotCommand("yordam", "Savol-javob va yordam"),
]


async def post_init(app: Application) -> None:
    await init_db()
    await app.bot.set_my_commands(COMMANDS)
    logger.info("Bot ishga tushdi.")


async def post_shutdown(app: Application) -> None:
    await close_db()


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Kutilmagan xato: %s", context.error, exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Kutilmagan xatolik yuz berdi. Iltimos, birozdan so'ng qayta urinib ko'ring."
            )
        except Exception:  # noqa: BLE001
            pass


def build_application(settings: Settings) -> Application:
    app = (
        Application.builder()
        .token(settings.bot_token)
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    private = filters.ChatType.PRIVATE
    app.add_handler(CommandHandler("start", start_handler.start, filters=private))
    app.add_handler(CommandHandler("menu", start_handler.menu, filters=private))
    app.add_handler(CommandHandler("bekor", cancel, filters=private))
    app.add_handler(CommandHandler(["yordam", "help"], help_handler.open_service, filters=private))
    for module in (weather, currency, converter, translate, reminders, tasks):
        for handler in module.HANDLERS:
            app.add_handler(handler)
    app.add_handler(MessageHandler(private & filters.TEXT & ~filters.COMMAND, route_text))
    app.add_error_handler(on_error)
    app.job_queue.run_repeating(check_due_reminders, interval=CHECK_INTERVAL, first=5)
    return app


def main() -> None:
    import asyncio

    # Python 3.14 da event loop avtomatik yaratilmaydi, shuning uchun o'zimiz yaratamiz
    asyncio.set_event_loop(asyncio.new_event_loop())

    settings = get_settings()
    setup_logging(settings.log_level)
    init_engine(settings.database_url)
    app = build_application(settings)
    if settings.webhook_url:
        base = settings.webhook_url.rstrip("/")
        logger.info("Webhook rejimi: port %s", settings.port)
        app.run_webhook(
            listen="0.0.0.0",
            port=settings.port,
            url_path="webhook",
            webhook_url=f"{base}/webhook",
            secret_token=settings.webhook_secret or None,
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        logger.info("Polling rejimi")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
