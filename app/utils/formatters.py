"""Matn, son va sana formatlash yordamchilari."""
from __future__ import annotations

import html
from datetime import datetime, timezone

from app.config import TZ

WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]


def esc(value) -> str:
    """Foydalanuvchi matnini HTML uchun xavfsiz qiladi."""
    return html.escape(str(value), quote=False)


def utcnow() -> datetime:
    """Hozirgi UTC vaqt (tz-siz) — bazada shunday saqlanadi."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_local(naive_utc: datetime) -> datetime:
    return naive_utc.replace(tzinfo=timezone.utc).astimezone(TZ)


def to_utc_naive(aware: datetime) -> datetime:
    return aware.astimezone(timezone.utc).replace(tzinfo=None)


def fmt_dt(local: datetime) -> str:
    return local.strftime("%d.%m.%Y %H:%M")


def fmt_num(value: float, digits: int = 2) -> str:
    """12345.6 -> '12 345,6' (o'zbekcha ko'rinish)."""
    text = f"{value:,.{digits}f}".replace(",", " ").replace(".", ",")
    if "," in text:
        text = text.rstrip("0").rstrip(",")
    return "0" if text in ("-0", "") else text


def weather_text(code: int | None) -> str:
    if code is None:
        return "Noma'lum"
    if code == 0:
        return "Ochiq osmon ☀️"
    if code == 1:
        return "Asosan ochiq 🌤"
    if code == 2:
        return "Qisman bulutli ⛅"
    if code == 3:
        return "Bulutli ☁️"
    if code in (45, 48):
        return "Tuman 🌫"
    if 51 <= code <= 57:
        return "Mayda yomg'ir 🌦"
    if 61 <= code <= 67:
        return "Yomg'ir 🌧"
    if 71 <= code <= 77 or code in (85, 86):
        return "Qor ❄️"
    if 80 <= code <= 82:
        return "Jala yomg'ir 🌧"
    if code >= 95:
        return "Momaqaldiroq ⛈"
    return "Noma'lum"


def format_weather(place: dict, data: dict) -> str:
    cur, daily = data["current"], data["daily"]
    country = place.get("country") or ""
    title = esc(place.get("name", "")) + (f", {esc(country)}" if country else "")
    lines = [
        f"🌍 <b>{title}</b>",
        "",
        f"<b>Hozir:</b> {weather_text(cur.get('weather_code'))}",
        f"🌡 {fmt_num(cur['temperature_2m'], 0)}°C "
        f"(his etilishi: {fmt_num(cur['apparent_temperature'], 0)}°C)",
        f"💧 Namlik: {fmt_num(cur['relative_humidity_2m'], 0)}%   "
        f"💨 Shamol: {fmt_num(cur['wind_speed_10m'], 1)} m/s",
        "",
        "<b>📅 Qisqa prognoz:</b>",
    ]
    probs = daily.get("precipitation_probability_max") or []
    for i, day in enumerate(daily["time"]):
        date = datetime.strptime(day, "%Y-%m-%d")
        label = "Bugun" if i == 0 else "Ertaga" if i == 1 else WEEKDAYS[date.weekday()]
        prob = probs[i] if i < len(probs) and probs[i] is not None else None
        prob_txt = f", yog'ingarchilik ehtimoli {fmt_num(prob, 0)}%" if prob is not None else ""
        lines.append(
            f"• <b>{label}</b> ({date:%d.%m}): {fmt_num(daily['temperature_2m_min'][i], 0)}…"
            f"{fmt_num(daily['temperature_2m_max'][i], 0)}°C, "
            f"{weather_text(daily['weather_code'][i])}{prob_txt}"
        )
    lines += ["", "<i>Manba: Open-Meteo</i>"]
    return "\n".join(lines)


MAIN_CURRENCIES = ["USD", "EUR", "RUB", "GBP", "KZT", "CNY", "TRY", "JPY", "KRW"]


def format_rates(rates: dict) -> str:
    lines = ["💱 <b>Valyuta kurslari</b> (O'zbekiston Markaziy banki)", ""]
    date = ""
    for code in MAIN_CURRENCIES:
        item = rates.get(code)
        if not item:
            continue
        date = date or item["date"]
        diff = item["diff"]
        arrow = "🔺" if diff > 0 else "🔻" if diff < 0 else "▫️"
        lines.append(
            f"<b>1 {code}</b> = {fmt_num(item['rate'])} so'm  {arrow} {fmt_num(abs(diff))}"
        )
    if date:
        lines += ["", f"📅 Kurs sanasi: {esc(date)}"]
    lines += [
        "",
        "💡 Hisoblash uchun yozing, masalan: <code>100 USD</code>",
        "<i>Manba: cbu.uz</i>",
    ]
    return "\n".join(lines)
