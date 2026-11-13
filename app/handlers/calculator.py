from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.common import back_cancel_keyboard
from app.services.calculator_service import CalcError, evaluate, format_result
from app.utils.formatters import esc

SERVICE = "calculator"
DIRECT_INPUT = True

INTRO = (
    "🧮 <b>Kalkulyator</b>\n\n"
    "Misolni yozing, masalan:\n"
    "<code>12*(3+4)</code>\n"
    "<code>2^10</code>\n"
    "<code>sqrt(144) + 15%4</code>\n\n"
    "Amallar: <code>+ − * / ^</code>, <code>%</code> (qoldiq), <code>//</code> (butun bo'lish), "
    "<code>sqrt()</code>, <code>abs()</code>, <code>pi</code>."
)


async def open_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["service"] = SERVICE
    context.user_data["state"] = "await_expr"
    await update.effective_message.reply_text(INTRO, reply_markup=back_cancel_keyboard())


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    expr = update.message.text.strip()
    try:
        result = format_result(evaluate(expr))
    except CalcError as exc:
        await update.message.reply_text(f"❌ {esc(exc)}")
        return
    await update.message.reply_text(f"<code>{esc(expr)}</code> = <b>{result}</b>")
