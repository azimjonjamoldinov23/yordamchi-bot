from __future__ import annotations

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CallbackQueryHandler, ContextTypes

from app.keyboards.common import back_cancel_keyboard, ibtn, inline
from app.services.http_client import ServiceError
from app.services.translation_service import LANGS, MAX_CHARS, translate
from app.utils.formatters import esc

SERVICE = "translate"
DIRECT_INPUT = False


def _langs_keyboard():
    items = [ibtn(label, f"tr:{key}") for key, (label, _) in LANGS.items()]
    return inline([items[i : i + 2] for i in range(0, len(items), 2)])


async def open_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["service"] = SERVICE
    context.user_data["state"] = None
    context.user_data.pop("lang", None)
    await update.effective_message.reply_text(
        "🌐 <b>Tarjima</b>\n\nQaysi tilga tarjima qilamiz? Tilni tanlang 👇",
        reply_markup=_langs_keyboard(),
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    if key not in LANGS:
        return
    context.user_data["service"] = SERVICE
    context.user_data["state"] = "await_text"
    context.user_data["lang"] = key
    await query.message.reply_text(
        f"Tanlangan til: <b>{LANGS[key][0]}</b>\n\n"
        f"Tarjima qilinadigan matnni yuboring (eng ko'pi bilan {MAX_CHARS} belgi). "
        "Asl til avtomatik aniqlanadi.",
        reply_markup=back_cancel_keyboard(),
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    lang = context.user_data.get("lang")
    if not lang:
        await open_service(update, context)
        return
    text = msg.text.strip()
    if len(text) > MAX_CHARS:
        await msg.reply_text(f"❌ Matn juda uzun ({len(text)} belgi). Eng ko'pi bilan {MAX_CHARS} belgi.")
        return
    await msg.chat.send_action(ChatAction.TYPING)
    try:
        result = await translate(text, lang)
    except ServiceError as exc:
        await msg.reply_text(f"⚠️ {esc(exc)}")
        return
    await msg.reply_text(
        f"🌐 <b>{LANGS[lang][0]}</b>\n\n{esc(result)}\n\n"
        "<i>Mashina tarjimasi — aniqligi kafolatlanmaydi. Manba: MyMemory</i>"
    )


HANDLERS = [CallbackQueryHandler(on_callback, pattern=r"^tr:")]
