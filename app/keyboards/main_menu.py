from __future__ import annotations

from telegram import ReplyKeyboardMarkup

MENU_ITEMS = [
    ("weather", "🌤 Ob-havo"),
    ("currency", "💱 Valyuta kurslari"),
    ("calculator", "🧮 Kalkulyator"),
    ("converter", "📐 Birliklar"),
    ("translate", "🌐 Tarjima"),
    ("reminders", "⏰ Eslatmalar"),
    ("tasks", "📝 Vazifalar"),
    ("help", "❓ Savol-javob"),
]
MENU_ACTIONS = {label: key for key, label in MENU_ITEMS}


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    labels = [label for _, label in MENU_ITEMS]
    rows = [labels[i : i + 2] for i in range(0, len(labels), 2)]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)
