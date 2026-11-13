"""O'zbekiston Markaziy banki (cbu.uz) rasmiy kurslari."""
from __future__ import annotations

import re

from app.services.http_client import ServiceError, get_json

CBU_URL = "https://cbu.uz/oz/arkhiv-kursov-valyut/json/"
_AMOUNT_RE = re.compile(r"^(\d+(?:[.,]\d+)?)\s*([A-Za-z]{3})$")


async def fetch_rates() -> dict[str, dict]:
    data = await get_json(CBU_URL)
    if not isinstance(data, list) or not data:
        raise ServiceError("Markaziy bank xizmati kurslarni qaytarmadi.")
    rates: dict[str, dict] = {}
    for item in data:
        try:
            nominal = float(item.get("Nominal") or 1) or 1.0
            rate = float(str(item["Rate"]).replace(",", ".")) / nominal
            diff = float(str(item.get("Diff") or 0).replace(",", ".")) / nominal
            rates[str(item["Ccy"]).upper()] = {
                "name": item.get("CcyNm_UZ") or item["Ccy"],
                "rate": rate,
                "diff": diff,
                "date": item.get("Date", ""),
            }
        except (KeyError, TypeError, ValueError):
            continue
    if not rates:
        raise ServiceError("Markaziy bank ma'lumotlarini o'qib bo'lmadi.")
    return rates


def parse_amount(text: str) -> tuple[float, str] | None:
    m = _AMOUNT_RE.match(text.strip())
    if not m:
        return None
    return float(m.group(1).replace(",", ".")), m.group(2).upper()
