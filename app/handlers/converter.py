from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from app.keyboards.common import back_cancel_keyboard, ibtn, inline
from app.services.converter_service import (
    CATEGORIES, EXAMPLES, HINTS, ConvertError, convert, parse_request,
)
from app.utils.formatters import esc, fmt_num

SERVICE = "converter"
DIRECT_INPUT = False


def _menu():
    return inline([[ibtn(label, f"cv:{key}")] for key, label in CATEGORIES.items()])


async def open_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["service"] = SERVICE
    context.user_data["state"] = None
    context.user_data.pop("category", None)
    await update.effective_message.reply_text(
        "📐 <b>Birliklarni aylantirish</b>\n\nKategoriyani tanlang:", reply_markup=_menu()
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    if key not in CATEGORIES:
        return
    context.user_data["service"] = SERVICE
    context.user_data["state"] = "await_value"
    context.user_data["category"] = key
    await query.message.reply_text(
        f"{CATEGORIES[key]}\n\nYozing: <code>qiymat birlik birlik</code>\n"
        f"Masalan: <code>{EXAMPLES[key]}</code>\n\n"
        f"Mavjud birliklar: {esc(HINTS[key])}",
        reply_markup=back_cancel_keyboard(),
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    category = context.user_data.get("category")
    if not category:
        await open_service(update, context)
        return
    try:
        value, src, dst = parse_request(update.message.text)
        result = convert(category, value, src, dst)
    except ConvertError as exc:
        await update.message.reply_text(f"❌ {esc(exc)}")
        return
    await update.message.reply_text(
        f"✅ {fmt_num(value, 6)} {esc(src)} = <b>{fmt_num(result, 6)} {esc(dst)}</b>"
    )


HANDLERS = [CallbackQueryHandler(on_callback, pattern=r"^cv:")]
