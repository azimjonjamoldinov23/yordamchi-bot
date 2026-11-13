"""Uzunlik, vazn va harorat birliklarini aylantirish."""
from __future__ import annotations

import re

# birlik -> bazaviy birlikka ko'paytiruvchi (uzunlik: metr, vazn: kilogramm)
LENGTH = {
    "mm": 0.001, "sm": 0.01, "cm": 0.01, "dm": 0.1, "m": 1.0, "km": 1000.0,
    "dyuym": 0.0254, "in": 0.0254, "fut": 0.3048, "ft": 0.3048,
    "yd": 0.9144, "yard": 0.9144, "mil": 1609.344, "mi": 1609.344,
}
MASS = {
    "mg": 1e-6, "g": 0.001, "gr": 0.001, "kg": 1.0, "t": 1000.0, "tonna": 1000.0,
    "oz": 0.028349523125, "unsiya": 0.028349523125, "lb": 0.45359237, "funt": 0.45359237,
}
TEMP = {
    "c": "c", "°c": "c", "selsiy": "c",
    "f": "f", "°f": "f", "farengeyt": "f",
    "k": "k", "kelvin": "k",
}

CATEGORIES = {
    "length": "📏 Uzunlik",
    "mass": "⚖️ Vazn",
    "temp": "🌡 Harorat",
}
HINTS = {
    "length": "mm, sm, dm, m, km, dyuym, fut, yd, mil",
    "mass": "mg, g, kg, t (tonna), oz, lb (funt)",
    "temp": "C (Selsiy), F (Farengeyt), K (Kelvin)",
}
EXAMPLES = {"length": "5 km mil", "mass": "70 kg lb", "temp": "25 C F"}

_NUM_RE = re.compile(r"^\s*(-?\d+(?:[.,]\d+)?)\s*(.*)$")
_FILLER = {"ga", "to", "->", "=", "→", "dan"}


class ConvertError(Exception):
    pass


def _norm_unit(token: str) -> str:
    for ch in "‘’ʻʼ`´":
        token = token.replace(ch, "'")
    return token.lower().strip(".")


def parse_request(text: str) -> tuple[float, str, str]:
    m = _NUM_RE.match(text)
    if not m:
        raise ConvertError("Avval son, so'ng ikkita birlikni yozing. Masalan: 5 km mil")
    value = float(m.group(1).replace(",", "."))
    tokens = [t for t in m.group(2).split() if t.lower() not in _FILLER]
    if len(tokens) != 2:
        raise ConvertError("Ikkita birlik kerak: qaysidan va qaysiga. Masalan: 5 km mil")
    return value, _norm_unit(tokens[0]), _norm_unit(tokens[1])


def convert(category: str, value: float, src: str, dst: str) -> float:
    if category in ("length", "mass"):
        table = LENGTH if category == "length" else MASS
        if src not in table or dst not in table:
            raise ConvertError(f"Noma'lum birlik. Mavjudlari: {HINTS[category]}")
        return value * table[src] / table[dst]
    if category == "temp":
        if src not in TEMP or dst not in TEMP:
            raise ConvertError(f"Noma'lum birlik. Mavjudlari: {HINTS['temp']}")
        s, d = TEMP[src], TEMP[dst]
        celsius = {"c": value, "f": (value - 32) * 5 / 9, "k": value - 273.15}[s]
        if celsius < -273.15 - 1e-9:
            raise ConvertError("Harorat mutlaq noldan (-273,15 °C) past bo'lishi mumkin emas.")
        return {"c": celsius, "f": celsius * 9 / 5 + 32, "k": celsius + 273.15}[d]
    raise ConvertError("Noma'lum kategoriya.")
