from __future__ import annotations

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CallbackQueryHandler, ContextTypes

from app.keyboards.common import back_cancel_keyboard, ibtn, inline
from app.services.currency_service import fetch_rates, parse_amount
from app.services.http_client import ServiceError
from app.utils.formatters import esc, fmt_num, format_rates
from app.utils.telegram_helpers import safe_edit

SERVICE = "currency"
DIRECT_INPUT = True


def _refresh_keyboard():
    return inline([[ibtn("🔄 Yangilash", "cur:refresh")]])


async def open_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["service"] = SERVICE
    context.user_data["state"] = "await_amount"
    msg = update.effective_message
    await msg.reply_text("💱 Kurslar yuklanmoqda…", reply_markup=back_cancel_keyboard())
    await msg.chat.send_action(ChatAction.TYPING)
    try:
        text = format_rates(await fetch_rates())
    except ServiceError as exc:
        text = f"⚠️ {esc(exc)}"
    await msg.reply_text(text, reply_markup=_refresh_keyboard())


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    parsed = parse_amount(msg.text)
    if not parsed:
        await msg.reply_text(
            "Summa va valyuta kodini yozing. Masalan: <code>100 USD</code> yoki <code>50 EUR</code>."
        )
        return
    amount, code = parsed
    try:
        rates = await fetch_rates()
    except ServiceError as exc:
        await msg.reply_text(f"⚠️ {esc(exc)}")
        return
    if code not in rates:
        await msg.reply_text(f"❌ «{esc(code)}» valyutasi Markaziy bank ro'yxatida topilmadi.")
        return
    total = amount * rates[code]["rate"]
    await msg.reply_text(
        f"💱 {fmt_num(amount)} {code} = <b>{fmt_num(total)} so'm</b>\n"
        f"<i>Kurs sanasi: {esc(rates[code]['date'])} · Manba: cbu.uz</i>"
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data["service"] = SERVICE
    context.user_data["state"] = "await_amount"
    try:
        text = format_rates(await fetch_rates())
    except ServiceError as exc:
        text = f"⚠️ {esc(exc)}"
    await safe_edit(query, text, _refresh_keyboard())


HANDLERS = [CallbackQueryHandler(on_callback, pattern=r"^cur:")]
