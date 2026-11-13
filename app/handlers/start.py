from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.main_menu import main_menu_keyboard
from app.utils.formatters import esc

WELCOME = (
    "Assalomu alaykum, <b>{name}</b>! 👋\n\n"
    "Men <b>Kunlik yordamchi</b> botman. Quyidagilarda yordam bera olaman:\n\n"
    "🌤 Ob-havo va qisqa prognoz\n"
    "💱 Markaziy bank valyuta kurslari\n"
    "🧮 Kalkulyator\n"
    "📐 Birliklarni aylantirish\n"
    "🌐 Tarjima\n"
    "⏰ Eslatmalar\n"
    "📝 Kunlik vazifalar\n"
    "❓ Savol-javob\n\n"
    "Kerakli xizmatni quyidagi menyudan tanlang 👇"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    name = update.effective_user.first_name if update.effective_user else "do'stim"
    await update.effective_message.reply_text(
        WELCOME.format(name=esc(name)), reply_markup=main_menu_keyboard()
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.effective_message.reply_text(
        "🏠 <b>Asosiy menyu</b>\nXizmatni tanlang 👇", reply_markup=main_menu_keyboard()
    )
