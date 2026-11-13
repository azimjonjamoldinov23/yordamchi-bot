from __future__ import annotations

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CallbackQueryHandler, ContextTypes

from app.keyboards.common import back_cancel_keyboard, ibtn, inline
from app.services.http_client import ServiceError
from app.services.weather_service import CityNotFound, get_weather
from app.utils.formatters import esc, format_weather

SERVICE = "weather"
DIRECT_INPUT = True
CITIES = ["Toshkent", "Samarqand", "Buxoro", "Andijon", "Namangan", "Farg'ona", "Nukus", "Qarshi"]


def _cities_keyboard():
    rows = [[ibtn(c, f"wx:{c}") for c in CITIES[i : i + 2]] for i in range(0, len(CITIES), 2)]
    return inline(rows)


async def open_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["service"] = SERVICE
    context.user_data["state"] = "await_city"
    msg = update.effective_message
    await msg.reply_text(
        "🌤 <b>Ob-havo</b>\n\nShahar nomini yozing (masalan: <i>Toshkent</i>) "
        "yoki quyidan tanlang 👇",
        reply_markup=back_cancel_keyboard(),
    )
    await msg.reply_text("Tezkor tanlov:", reply_markup=_cities_keyboard())


async def _show(update: Update, city: str) -> None:
    msg = update.effective_message
    await msg.chat.send_action(ChatAction.TYPING)
    try:
        place, data = await get_weather(city)
        text = format_weather(place, data)
    except CityNotFound:
        text = (
            f"❌ «{esc(city[:60])}» shahri topilmadi. Yozilishini tekshiring "
            "yoki boshqa yirik shahar nomini kiriting."
        )
    except ServiceError as exc:
        text = f"⚠️ {esc(exc)}"
    except (KeyError, TypeError, ValueError):
        text = "⚠️ Ob-havo ma'lumotini o'qib bo'lmadi. Birozdan so'ng qayta urinib ko'ring."
    await msg.reply_text(text)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _show(update, update.message.text)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data["service"] = SERVICE
    context.user_data["state"] = "await_city"
    await _show(update, query.data.split(":", 1)[1])


HANDLERS = [CallbackQueryHandler(on_callback, pattern=r"^wx:")]
