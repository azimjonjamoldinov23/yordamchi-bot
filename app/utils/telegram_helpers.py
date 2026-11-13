from __future__ import annotations

from telegram.error import BadRequest


async def safe_edit(query, text: str, reply_markup=None) -> None:
    """Xabarni tahrirlaydi; matn o'zgarmagan bo'lsa xatoni e'tiborsiz qoldiradi."""
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as exc:
        if "not modified" not in str(exc).lower():
            raise
