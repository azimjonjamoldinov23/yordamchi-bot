from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from app.database import repositories as repo
from app.keyboards.common import back_cancel_keyboard, ibtn, inline
from app.keyboards.main_menu import main_menu_keyboard
from app.utils.formatters import esc
from app.utils.telegram_helpers import safe_edit

SERVICE = "tasks"
DIRECT_INPUT = False
MAX_TASKS = 100
MAX_TITLE = 200


def _short(text: str, limit: int = 28) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


async def _render(user_id: int):
    tasks = await repo.list_tasks(user_id)
    rows = []
    if not tasks:
        text = "📝 <b>Kunlik vazifalar</b>\n\nHozircha vazifa yo'q. Birinchisini qo'shing 👇"
    else:
        done = sum(1 for t in tasks if t.done)
        lines = [f"📝 <b>Kunlik vazifalar</b> ({done}/{len(tasks)} bajarildi)", ""]
        for t in tasks:
            lines.append(f"✅ <s>{esc(t.title)}</s>" if t.done else f"⬜️ {esc(t.title)}")
        lines += ["", "<i>Tugma orqali belgilang yoki o'chiring.</i>"]
        text = "\n".join(lines)
        for t in tasks:
            mark = "↩️ " if t.done else "✅ "
            rows.append([ibtn(mark + _short(t.title), f"tk:t:{t.id}"), ibtn("🗑", f"tk:d:{t.id}")])
        if done:
            rows.append([ibtn("🧹 Bajarilganlarni tozalash", "tk:c")])
    rows.append([ibtn("➕ Vazifa qo'shish", "tk:add")])
    return text, inline(rows)


async def open_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["service"] = SERVICE
    context.user_data["state"] = None
    text, markup = await _render(update.effective_user.id)
    await update.effective_message.reply_text(text, reply_markup=markup)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    parts = query.data.split(":")
    action = parts[1]
    context.user_data["service"] = SERVICE

    if action == "add":
        if await repo.count_tasks(user_id) >= MAX_TASKS:
            await query.message.reply_text(f"❌ Vazifalar soni {MAX_TASKS} tadan oshmasligi kerak.")
            return
        context.user_data["state"] = "await_title"
        await query.message.reply_text(
            "➕ Vazifa matnini yuboring (masalan: <i>Dokonga borish</i>).",
            reply_markup=back_cancel_keyboard(),
        )
        return
    if action == "t" and len(parts) == 3 and parts[2].isdigit():
        await repo.toggle_task(user_id, int(parts[2]))
    elif action == "d" and len(parts) == 3 and parts[2].isdigit():
        await repo.delete_task(user_id, int(parts[2]))
    elif action == "c":
        await repo.clear_done_tasks(user_id)
    text, markup = await _render(user_id)
    await safe_edit(query, text, markup)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    title = " ".join(update.message.text.split())
    if not title:
        await update.message.reply_text("❌ Vazifa matni bo'sh bo'lmasligi kerak.")
        return
    if len(title) > MAX_TITLE:
        await update.message.reply_text(f"❌ Vazifa matni {MAX_TITLE} belgidan oshmasligi kerak.")
        return
    await repo.add_task(update.effective_user.id, title)
    context.user_data["state"] = None
    await update.message.reply_text("✅ Vazifa qo'shildi.", reply_markup=main_menu_keyboard())
    await open_service(update, context)


HANDLERS = [CallbackQueryHandler(on_callback, pattern=r"^tk:")]
