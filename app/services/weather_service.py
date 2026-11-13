"""Open-Meteo orqali ob-havo (API kalit talab qilinmaydi)."""
from __future__ import annotations

from app.services.http_client import ServiceError, get_json

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

ALIASES = {
    "toshkent": "Tashkent", "samarqand": "Samarkand", "buxoro": "Bukhara",
    "andijon": "Andijan", "namangan": "Namangan", "farg'ona": "Fergana",
    "nukus": "Nukus", "qarshi": "Karshi", "urganch": "Urgench", "termiz": "Termez",
    "jizzax": "Jizzakh", "navoiy": "Navoi", "guliston": "Gulistan", "xiva": "Khiva",
    "qo'qon": "Kokand", "margilon": "Margilan", "angren": "Angren", "chirchiq": "Chirchiq",
}


class CityNotFound(Exception):
    pass


def _clean(name: str) -> str:
    for ch in "‘’ʻʼ`´":
        name = name.replace(ch, "'")
    return " ".join(name.split())


async def find_city(name: str) -> dict:
    cleaned = _clean(name)
    if not cleaned or len(cleaned) > 60:
        raise CityNotFound
    query = ALIASES.get(cleaned.lower(), cleaned)
    data = await get_json(
        GEOCODE_URL, params={"name": query, "count": 1, "language": "en", "format": "json"}
    )
    results = data.get("results") if isinstance(data, dict) else None
    if not results:
        raise CityNotFound
    return results[0]


async def get_weather(city: str) -> tuple[dict, dict]:
    place = await find_city(city)
    data = await get_json(
        FORECAST_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
            "forecast_days": 4,
            "wind_speed_unit": "ms",
        },
    )
    if not isinstance(data, dict) or "current" not in data or "daily" not in data:
        raise ServiceError("Ob-havo xizmati to'liq bo'lmagan ma'lumot qaytardi.")
    return place, data
