"""Log sozlamalari. Token va maxfiy qiymatlar loglardan avtomatik yashiriladi."""
from __future__ import annotations

import logging
import re

_TOKEN_RE = re.compile(r"\d{6,}:[A-Za-z0-9_-]{30,}")
_SECRET_RE = re.compile(r"(?i)(token|password|parol|secret|api[_-]?key)(=|:\s*)\S+")


def redact(text: str) -> str:
    text = _TOKEN_RE.sub("[YASHIRILGAN]", text)
    return _SECRET_RE.sub(r"\1\2[YASHIRILGAN]", text)


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return redact(super().format(record))


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        RedactingFormatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
    # httpx so'rov URL'larini (ichida bot tokeni bor) INFO darajasida yozadi
    for name in ("httpx", "httpcore", "hpack"):
        logging.getLogger(name).setLevel(logging.WARNING)
