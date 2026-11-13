"""Sof mantiq testlari (tarmoq va Telegram talab qilinmaydi). Ishga tushirish: pytest"""
from datetime import datetime

import pytest

from app.config import TZ, normalize_database_url
from app.handlers.help import find_answer
from app.logging_config import redact
from app.services.calculator_service import CalcError, evaluate, format_result
from app.services.converter_service import ConvertError, convert, parse_request
from app.utils.formatters import fmt_num
from app.utils.validators import parse_reminder

NOW = datetime(2026, 11, 7, 12, 0, tzinfo=TZ)


def test_calculator():
    assert evaluate("12*(3+4)") == 84
    assert evaluate("2^10") == 1024
    assert format_result(evaluate("10/4")) == "2,5"
    assert evaluate("sqrt(144)+15%4") == 15
    for bad in ("1/0", "__import__('os')", "2**99999", "abc"):
        with pytest.raises(CalcError):
            evaluate(bad)


def test_converter():
    assert convert("length", 1, "km", "m") == 1000
    assert round(convert("temp", 100, "c", "f")) == 212
    assert round(convert("mass", 1, "kg", "lb"), 3) == 2.205
    assert parse_request("5 km ga mil") == (5.0, "km", "mil")
    with pytest.raises(ConvertError):
        convert("temp", -300, "c", "k")
    with pytest.raises(ConvertError):
        convert("length", 1, "km", "kg")


def test_reminder_parsing():
    when, text = parse_reminder("30 daqiqadan keyin Choy", NOW)
    assert text == "Choy" and (when - NOW).seconds == 1800
    when, _ = parse_reminder("ertaga 09:00 Yig'ilish", NOW)
    assert (when.day, when.hour) == (8, 9)
    when, _ = parse_reminder("10:00 Ertalabki", NOW)  # o'tib ketgan -> ertaga
    assert when.day == 8
    when, _ = parse_reminder("15.11.2026 14:00 Tug'ilgan kun", NOW)
    assert (when.month, when.day, when.hour) == (11, 15, 14)
    for bad in ("salom", "01.01.2020 10:00 eski", "32.13.2026 10:00 xato", "18:30"):
        with pytest.raises(ValueError):
            parse_reminder(bad, NOW)


def test_misc():
    assert fmt_num(12345.6) == "12 345,6"
    assert normalize_database_url("postgres://u:p@h/db").startswith("postgresql+asyncpg://")
    assert "[YASHIRILGAN]" in redact("url=https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz0123456789/getMe")
    assert "ishonchli" in find_answer("Qirol Artur haqida gapir")
    assert "cbu.uz" in find_answer("Kurslar qayerdan olinadi?")
