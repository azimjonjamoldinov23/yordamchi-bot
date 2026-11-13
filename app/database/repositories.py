"""Baza bilan ishlash funksiyalari (eslatmalar va vazifalar)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, select, update

from app.database.connection import session_scope
from app.database.models import Reminder, Task

# ---------------------------------------------------------------- Eslatmalar


async def add_reminder(user_id: int, text: str, remind_at_utc: datetime) -> Reminder:
    async with session_scope() as s:
        item = Reminder(user_id=user_id, text=text, remind_at=remind_at_utc)
        s.add(item)
        await s.flush()
        return item


async def list_reminders(user_id: int) -> list[Reminder]:
    async with session_scope() as s:
        rows = await s.scalars(
            select(Reminder)
            .where(Reminder.user_id == user_id, Reminder.sent.is_(False))
            .order_by(Reminder.remind_at)
        )
        return list(rows)


async def count_pending_reminders(user_id: int) -> int:
    async with session_scope() as s:
        return (
            await s.scalar(
                select(func.count())
                .select_from(Reminder)
                .where(Reminder.user_id == user_id, Reminder.sent.is_(False))
            )
        ) or 0


async def delete_reminder(user_id: int, reminder_id: int) -> bool:
    async with session_scope() as s:
        res = await s.execute(
            delete(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id,
                Reminder.sent.is_(False),
            )
        )
        return (res.rowcount or 0) > 0


async def due_reminders(now_utc: datetime, limit: int = 100) -> list[Reminder]:
    async with session_scope() as s:
        rows = await s.scalars(
            select(Reminder)
            .where(Reminder.sent.is_(False), Reminder.remind_at <= now_utc)
            .order_by(Reminder.remind_at)
            .limit(limit)
        )
        return list(rows)


async def mark_reminder_sent(reminder_id: int) -> None:
    async with session_scope() as s:
        await s.execute(update(Reminder).where(Reminder.id == reminder_id).values(sent=True))


# ------------------------------------------------------------------ Vazifalar


async def add_task(user_id: int, title: str) -> Task:
    async with session_scope() as s:
        item = Task(user_id=user_id, title=title)
        s.add(item)
        await s.flush()
        return item


async def list_tasks(user_id: int) -> list[Task]:
    async with session_scope() as s:
        rows = await s.scalars(
            select(Task).where(Task.user_id == user_id).order_by(Task.done, Task.id)
        )
        return list(rows)


async def count_tasks(user_id: int) -> int:
    async with session_scope() as s:
        return (
            await s.scalar(select(func.count()).select_from(Task).where(Task.user_id == user_id))
        ) or 0


async def toggle_task(user_id: int, task_id: int) -> bool:
    async with session_scope() as s:
        task = await s.scalar(select(Task).where(Task.id == task_id, Task.user_id == user_id))
        if task is None:
            return False
        task.done = not task.done
        return True


async def delete_task(user_id: int, task_id: int) -> bool:
    async with session_scope() as s:
        res = await s.execute(delete(Task).where(Task.id == task_id, Task.user_id == user_id))
        return (res.rowcount or 0) > 0


async def clear_done_tasks(user_id: int) -> int:
    async with session_scope() as s:
        res = await s.execute(delete(Task).where(Task.user_id == user_id, Task.done.is_(True)))
        return res.rowcount or 0
