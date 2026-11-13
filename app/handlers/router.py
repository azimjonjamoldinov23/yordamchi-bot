"""Matnli xabarlarni menyu tugmalari va faol xizmatga yo'naltiradi."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.handlers import calculator, converter, currency, help, reminders, tasks, translate, weather
from app.keyboards.common import BTN_BACK, BTN_CANCEL
from app.keyboards.main_menu import MENU_ACTIONS, main_menu_keyboard

SERVICES = {
    "weather": weather, "currency": currency, "calculator": calculator, "converter": converter,
    "translate": translate, "reminders": reminders, "tasks": tasks, "help": help,
}


async def go_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.effective_message.reply_text(
        "🏠 <b>Asosiy menyu</b>\nXizmatni tanlang 👇", reply_markup=main_menu_keyboard()
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Joriy amalni bekor qiladi: xizmat menyusiga (yoki asosiy menyuga) qaytaradi."""
    key = context.user_data.get("service")
    module = SERVICES.get(key)
    context.user_data.clear()
    if module is None or getattr(module, "DIRECT_INPUT", False):
        await update.effective_message.reply_text(
            "❌ Bekor qilindi.\n\n🏠 <b>Asosiy menyu</b>", reply_markup=main_menu_keyboard()
        )
        return
    await update.effective_message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard())
    await module.open_service(update, context)


async def route_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if text == BTN_BACK:
        await go_main(update, context)
        return
    if text == BTN_CANCEL:
        await cancel(update, context)
        return
    key = MENU_ACTIONS.get(text)
    if key:
        context.user_data.clear()
        await SERVICES[key].open_service(update, context)
        return
    service = context.user_data.get("service")
    if service in SERVICES and context.user_data.get("state"):
        await SERVICES[service].on_text(update, context)
        return
    await update.message.reply_text(
        "Iltimos, menyudan xizmatni tanlang 👇", reply_markup=main_menu_keyboard()
    )
