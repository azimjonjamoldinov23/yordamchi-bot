"""MyMemory orqali tarjima (bepul, API kalitsiz; kunlik limit bor)."""
from __future__ import annotations

import html

from app.config import get_settings
from app.services.http_client import ServiceError, get_json

URL = "https://api.mymemory.translated.net/get"
MAX_CHARS = 450

# kalit -> (ko'rsatiladigan nom, MyMemory kodi)
LANGS = {
    "en": ("🇬🇧 Inglizcha", "en"),
    "ru": ("🇷🇺 Ruscha", "ru"),
    "tr": ("🇹🇷 Turkcha", "tr"),
    "ar": ("🇸🇦 Arabcha", "ar"),
    "de": ("🇩🇪 Nemischa", "de"),
    "fr": ("🇫🇷 Fransuzcha", "fr"),
    "es": ("🇪🇸 Ispancha", "es"),
    "ko": ("🇰🇷 Koreyscha", "ko"),
    "zh": ("🇨🇳 Xitoycha", "zh-CN"),
    "uz": ("🇺🇿 O'zbekcha", "uz"),
}


async def translate(text: str, lang_key: str) -> str:
    if lang_key not in LANGS:
        raise ServiceError("Noma'lum til tanlandi.")
    params = {"q": text, "langpair": f"Autodetect|{LANGS[lang_key][1]}"}
    email = get_settings().mymemory_email
    if email:
        params["de"] = email
    data = await get_json(URL, params=params)
    try:
        status = str(data.get("responseStatus"))
        result = data["responseData"]["translatedText"]
    except (AttributeError, KeyError, TypeError):
        raise ServiceError("Tarjima xizmati noto'g'ri javob qaytardi.") from None
    if "MYMEMORY WARNING" in str(result).upper():
        raise ServiceError("Tarjima xizmatining bugungi bepul limiti tugagan. Keyinroq urinib ko'ring.")
    if status != "200" or not result:
        raise ServiceError("Tarjimani bajarib bo'lmadi. Matnni o'zgartirib qayta urinib ko'ring.")
    return html.unescape(str(result))
