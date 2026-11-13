"""Eslatmalarni yuborish mexanizmi.

Eslatmalar bazada saqlanadi. JobQueue har CHECK_INTERVAL soniyada muddati
kelgan eslatmalarni topib yuboradi. Bot o'chib yonsa ham eslatmalar yo'qolmaydi.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import ContextTypes

from app.database import repositories as repo
from app.utils.formatters import esc, utcnow

logger = logging.getLogger(__name__)
CHECK_INTERVAL = 30  # soniya
LATE_AFTER = timedelta(minutes=5)


async def check_due_reminders(context: ContextTypes.DEFAULT_TYPE) -> None:
    now = utcnow()
    try:
        due = await repo.due_reminders(now)
    except Exception:
        logger.exception("Eslatmalarni bazadan o'qib bo'lmadi")
        return
    for item in due:
        late = now - item.remind_at > LATE_AFTER
        text = f"⏰ <b>Eslatma</b>\n\n{esc(item.text)}"
        if late:
            text += "\n\n<i>(Bot o'chiq bo'lgani uchun kechikib yuborildi)</i>"
        try:
            await context.bot.send_message(chat_id=item.user_id, text=text)
        except (Forbidden, BadRequest):
            logger.info("Eslatma #%s yuborib bo'lmadi (foydalanuvchi botni bloklagan)", item.id)
        except TelegramError:
            logger.warning("Eslatma #%s vaqtincha yuborilmadi, keyingi urinishda qaytadan", item.id)
            continue
        await repo.mark_reminder_sent(item.id)
