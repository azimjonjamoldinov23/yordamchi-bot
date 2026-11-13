from __future__ import annotations

from datetime import datetime

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from app.config import TZ
from app.database import repositories as repo
from app.keyboards.common import back_cancel_keyboard, ibtn, inline
from app.keyboards.main_menu import main_menu_keyboard
from app.utils.formatters import esc, fmt_dt, to_local, to_utc_naive
from app.utils.telegram_helpers import safe_edit
from app.utils.validators import parse_reminder

SERVICE = "reminders"
DIRECT_INPUT = False
MAX_PENDING = 50

FORMAT_HELP = (
    "Quyidagi formatlardan birida yozing:\n"
    "• <code>18:30 Dori ichish</code> — bugun (o'tib ketgan bo'lsa, ertaga)\n"
    "• <code>ertaga 09:00 Yig'ilish</code>\n"
    "• <code>15.11.2026 14:00 Tug'ilgan kun</code>\n"
    "• <code>30 daqiqadan keyin Choy qo'yish</code>\n"
    "• <code>2 soatdan keyin Qo'ng'iroq qilish</code>\n\n"
    "Vaqt <b>Toshkent vaqti</b> bo'yicha hisoblanadi."
)


def _menu():
    return inline([[ibtn("➕ Yangi eslatma", "rm:new")], [ibtn("📋 Eslatmalarim", "rm:list")]])


async def open_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["service"] = SERVICE
    context.user_data["state"] = None
    await update.effective_message.reply_text(
        "⏰ <b>Eslatmalar</b>\n\nNima qilmoqchisiz?", reply_markup=_menu()
    )


async def _render_list(user_id: int):
    items = await repo.list_reminders(user_id)
    if not items:
        return "📋 Sizda hozircha faol eslatma yo'q.", _menu()
    lines = ["📋 <b>Faol eslatmalar</b>", ""]
    rows = []
    for n, item in enumerate(items, 1):
        lines.append(f"{n}. <b>{fmt_dt(to_local(item.remind_at))}</b> — {esc(item.text)}")
        rows.append([ibtn(f"🗑 {n}-eslatmani o'chirish", f"rm:del:{item.id}")])
    rows.append([ibtn("➕ Yangi eslatma", "rm:new")])
    return "\n".join(lines), inline(rows)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    parts = query.data.split(":")
    action = parts[1]
    context.user_data["service"] = SERVICE

    if action == "new":
        if await repo.count_pending_reminders(user_id) >= MAX_PENDING:
            await query.message.reply_text(
                f"❌ Faol eslatmalar soni {MAX_PENDING} tadan oshmasligi kerak. Avval ba'zilarini o'chiring."
            )
            return
        context.user_data["state"] = "await_text"
        await query.message.reply_text(
            "➕ <b>Yangi eslatma</b>\n\n" + FORMAT_HELP, reply_markup=back_cancel_keyboard()
        )
    elif action == "list":
        text, markup = await _render_list(user_id)
        await safe_edit(query, text, markup)
    elif action == "del" and len(parts) == 3 and parts[2].isdigit():
        deleted = await repo.delete_reminder(user_id, int(parts[2]))
        text, markup = await _render_list(user_id)
        await safe_edit(query, ("🗑 Eslatma o'chirildi.\n\n" if deleted else "") + text, markup)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    try:
        when_local, text = parse_reminder(msg.text, datetime.now(TZ))
    except ValueError as exc:
        await msg.reply_text(f"❌ {esc(exc)}\n\n{FORMAT_HELP}")
        return
    user_id = update.effective_user.id
    if await repo.count_pending_reminders(user_id) >= MAX_PENDING:
        await msg.reply_text(f"❌ Faol eslatmalar soni {MAX_PENDING} tadan oshmasligi kerak.")
        return
    await repo.add_reminder(user_id, text, to_utc_naive(when_local))
    context.user_data["state"] = None
    await msg.reply_text(
        f"✅ Eslatma saqlandi!\n\n⏰ <b>{fmt_dt(when_local)}</b> (Toshkent vaqti)\n📝 {esc(text)}",
        reply_markup=main_menu_keyboard(),
    )
    await open_service(update, context)


HANDLERS = [CallbackQueryHandler(on_callback, pattern=r"^rm:")]
