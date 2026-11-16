from typing import Optional, Tuple

from src.ext.database import db


class WhoopSchedule(db.Model):
    """Daily import time in UTC (single row)."""

    __tablename__ = "whoop_schedule"

    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.Integer, nullable=False)
    minute = db.Column(db.Integer, nullable=False)


def save_schedule(hour: int, minute: int) -> None:
    row = WhoopSchedule.query.first()
    if row is None:
        row = WhoopSchedule()
    row.hour = hour
    row.minute = minute
    db.session.add(row)
    db.session.commit()


def load_schedule() -> Optional[Tuple[int, int]]:
    row = WhoopSchedule.query.first()
    if row is None:
        return None
    return row.hour, row.minute


def clear_schedule() -> None:
    WhoopSchedule.query.delete()
    db.session.commit()
