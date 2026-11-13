"""Foydali savol-javob: faqat botning o'zi haqidagi tasdiqlangan ma'lumotlar.

Bot bilmagan narsani o'ylab topmaydi: mos javob bo'lmasa, buni ochiq aytadi
va savolni aniqlashtirishni so'raydi.
"""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.common import back_cancel_keyboard
from app.utils.formatters import esc

SERVICE = "help"
DIRECT_INPUT = True

TOPICS = "ob-havo, valyuta, kalkulyator, birliklar, tarjima, eslatmalar, vazifalar, maxfiylik, vaqt mintaqasi"

INTRO = (
    "❓ <b>Savol-javob</b>\n\n"
    "Men quyidagi mavzularda aniq javob bera olaman:\n"
    f"<i>{TOPICS}</i>.\n\n"
    "Savolingizni yozing. Aniq bilmagan narsamni o'ylab topmayman — "
    "bu holatda ochiq aytaman yoki savolni aniqlashtirishni so'rayman."
)

FAQ: list[tuple[tuple[str, ...], str]] = [
    (("ob-havo", "obhavo", "havo", "prognoz", "harorat"),
     "🌤 Ob-havo Open-Meteo xizmatidan olinadi: hozirgi holat va 4 kunlik qisqa prognoz. "
     "Shahar nomini yozing yoki tugmalardan tanlang. Shahar topilmasa, yozilishini tekshiring."),
    (("valyuta", "kurs", "dollar", "markaziy bank", "cbu", "yevro", "rubl"),
     "💱 Kurslar O'zbekiston Markaziy bankining rasmiy ochiq ma'lumotlaridan (cbu.uz) olinadi. "
     "Bu rasmiy kurs — bank yoki almashtirish shoxobchalari kursidan farq qilishi mumkin. "
     "Summani hisoblash uchun masalan <code>100 USD</code> deb yozing."),
    (("eslatma", "eslat", "ogohlantir"),
     "⏰ Eslatma yaratish: <code>18:30 matn</code>, <code>ertaga 09:00 matn</code>, "
     "<code>15.11.2026 14:00 matn</code> yoki <code>30 daqiqadan keyin matn</code>. "
     "Vaqt Toshkent vaqti bo'yicha. Eslatmalar bazada saqlanadi va muddati kelganda yuboriladi."),
    (("vazifa", "topshiriq", "reja", "bajarildi"),
     "📝 «Vazifalar» bo'limida vazifa qo'shish, bajarildi deb belgilash, o'chirish va ro'yxatni ko'rish mumkin."),
    (("kalkulyator", "hisobla", "hisob-kitob", "amal"),
     "🧮 Kalkulyator + − * / ^ % // amallari, qavslar, sqrt(), abs() va pi ni qo'llaydi. Masalan: <code>12*(3+4)</code>."),
    (("birlik", "aylantir", "konvert", "metr", "kilogram"),
     "📐 Uzunlik (mm…mil), vazn (mg…funt) va harorat (C, F, K) birliklarini aylantiradi. Masalan: <code>5 km mil</code>."),
    (("tarjima", "tillar", "tilga"),
     "🌐 Tarjima MyMemory xizmati orqali bajariladi (mashina tarjimasi, aniqligi kafolatlanmaydi). "
     "Asl til avtomatik aniqlanadi; bepul xizmatda kunlik limit bor."),
    (("maxfiy", "xavfsiz", "ma'lumotlarim", "saqla"),
     "🔒 Faqat eslatma va vazifalaringiz (matni va vaqti) botning alohida bazasida saqlanadi. "
     "Ularni istalgan payt o'zingiz o'chira olasiz."),
    (("vaqt mintaqa", "soat qayer", "toshkent vaqti", "timezone"),
     "🕒 Barcha sana va vaqtlar Asia/Tashkent vaqt mintaqasi bo'yicha ishlaydi."),
]


def _norm(text: str) -> str:
    for ch in "‘’ʻʼ`´":
        text = text.replace(ch, "'")
    return text.lower()


def find_answer(question: str) -> str:
    q = _norm(question)
    scored = sorted(
        ((sum(1 for k in kws if k in q), ans) for kws, ans in FAQ),
        key=lambda x: x[0],
        reverse=True,
    )
    top = scored[0][0]
    if top == 0:
        return (
            "🤔 Bu savolga aniq va ishonchli javob bera olmayman, taxmin qilib noto'g'ri ma'lumot bermayman.\n\n"
            f"Men quyidagi mavzularni bilaman: <i>{TOPICS}</i>.\n\n"
            "Qaysi xizmat yoki mavzu haqida so'rayapsiz? Boshqa masalalarda ishonchli rasmiy manbalarga murojaat qiling."
        )
    best = [a for s, a in scored if s == top]
    if len(best) > 1:
        return (
            "Savolingiz bir nechta mavzuga mos keldi. Aniqroq yozing: qaysi xizmat haqida so'rayapsiz?\n"
            f"<i>{TOPICS}</i>"
        )
    return best[0]


async def open_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["service"] = SERVICE
    context.user_data["state"] = "await_question"
    await update.effective_message.reply_text(INTRO, reply_markup=back_cancel_keyboard())


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(find_answer(update.message.text))
