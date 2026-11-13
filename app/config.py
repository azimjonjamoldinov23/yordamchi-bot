"""Sozlamalar: barcha qiymatlar .env yoki muhit o'zgaruvchilaridan o'qiladi."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

TZ = ZoneInfo("Asia/Tashkent")


def normalize_database_url(url: str) -> str:
    """Oddiy URL'larni SQLAlchemy asinxron drayverlariga moslaydi."""
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    if url.startswith("sqlite:///") and "aiosqlite" not in url:
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    log_level: str
    http_timeout: float
    mymemory_email: str
    webhook_url: str
    webhook_secret: str
    port: int


@lru_cache
def get_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN topilmadi. .env faylini yarating va tokenni kiriting."
        )
    return Settings(
        bot_token=token,
        database_url=normalize_database_url(
            os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/bot.db").strip()
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        http_timeout=float(os.getenv("HTTP_TIMEOUT", "10")),
        mymemory_email=os.getenv("MYMEMORY_EMAIL", "").strip(),
        webhook_url=os.getenv("WEBHOOK_URL", "").strip(),
        webhook_secret=os.getenv("WEBHOOK_SECRET", "").strip(),
        port=int(os.getenv("PORT", "8080")),
    )
