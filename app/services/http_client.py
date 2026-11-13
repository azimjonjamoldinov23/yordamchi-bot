"""Tashqi API'lar uchun umumiy so'rov funksiyasi: timeout, xato va qayta urinish."""
from __future__ import annotations

import asyncio
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """Foydalanuvchiga ko'rsatish mumkin bo'lgan o'zbekcha xabar bilan xato."""


async def get_json(url: str, *, params: dict | None = None, retries: int = 2):
    settings = get_settings()
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(
                timeout=settings.http_timeout,
                headers={"User-Agent": "daily-helper-bot/1.0"},
                follow_redirects=True,
            ) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code < 500:
                logger.warning("Tashqi xizmat %s holat kodi qaytardi", exc.response.status_code)
                raise ServiceError(
                    "Xizmat so'rovni qabul qilmadi. Birozdan so'ng qayta urinib ko'ring."
                ) from None
            last_error = exc
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            last_error = exc
        except ValueError:
            raise ServiceError("Xizmat noto'g'ri formatdagi javob qaytardi.") from None
        if attempt < retries:
            await asyncio.sleep(0.7 * (attempt + 1))
    logger.warning("Tashqi xizmat ishlamadi: %s", type(last_error).__name__)
    raise ServiceError(
        "Tashqi xizmat hozir javob bermayapti. Iltimos, birozdan so'ng qayta urinib ko'ring."
    )
