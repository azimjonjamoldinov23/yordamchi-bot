"""Foydalanuvchi kiritgan matnni tekshirish va tahlil qilish."""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from app.config import TZ

MAX_REMINDER_TEXT = 300

_ABS_RE = re.compile(r"^(\d{1,2})[./](\d{1,2})[./](\d{4})\s+(\d{1,2})[:.](\d{2})\s+(.+)$", re.S)
_REL_RE = re.compile(r"^(\d{1,4})\s*(daqiqa|daq|minut|min|soat|kun)\w*\s+keyin\s+(.+)$", re.S | re.I)
_TOMORROW_RE = re.compile(r"^ertaga\s+(\d{1,2}):(\d{2})\s+(.+)$", re.S | re.I)
_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})\s+(.+)$", re.S)


def parse_reminder(raw: str, now_local: datetime | None = None) -> tuple[datetime, str]:
    """Eslatma matnidan (vaqt, matn) ajratadi. Xatoda ValueError (o'zbekcha xabar)."""
    now = now_local or datetime.now(TZ)
    s = " ".join(raw.split())

    try:
        if m := _ABS_RE.match(s):
            d, mo, y, h, mi, text = m.groups()
            when = datetime(int(y), int(mo), int(d), int(h), int(mi), tzinfo=TZ)
        elif m := _REL_RE.match(s):
            amount, unit, text = m.groups()
            unit = unit.lower()
            if unit.startswith("d") or unit.startswith("m"):
                delta = timedelta(minutes=int(amount))
            elif unit == "soat":
                delta = timedelta(hours=int(amount))
            else:
                delta = timedelta(days=int(amount))
            when = (now + delta).replace(second=0, microsecond=0)
        elif m := _TOMORROW_RE.match(s):
            h, mi, text = m.groups()
            when = (now + timedelta(days=1)).replace(
                hour=int(h), minute=int(mi), second=0, microsecond=0
            )
        elif m := _TIME_RE.match(s):
            h, mi, text = m.groups()
            when = now.replace(hour=int(h), minute=int(mi), second=0, microsecond=0)
            if when <= now:
                when += timedelta(days=1)
        else:
            raise ValueError("Kiritilgan format tushunarsiz.")
    except OverflowError:
        raise ValueError("Vaqt noto'g'ri kiritildi.") from None
    except ValueError as exc:
        if str(exc) == "Kiritilgan format tushunarsiz.":
            raise
        raise ValueError("Sana yoki vaqt noto'g'ri kiritildi.") from None

    text = text.strip()
    if not text:
        raise ValueError("Eslatma matni bo'sh bo'lmasligi kerak.")
    if len(text) > MAX_REMINDER_TEXT:
        raise ValueError(f"Eslatma matni {MAX_REMINDER_TEXT} belgidan oshmasligi kerak.")
    if when <= now:
        raise ValueError("Bu vaqt allaqachon o'tib ketgan. Kelajakdagi vaqtni kiriting.")
    if when - now > timedelta(days=366):
        raise ValueError("Eslatmani 1 yildan uzoq muddatga qo'yib bo'lmaydi.")
    return when, text
