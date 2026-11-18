from enum import Enum
from datetime import datetime
from typing import Callable, Optional

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ImportTask:
    model: type
    callable: Callable
    start: Optional[datetime] = None
    retried_after_401: bool = field(default=False, compare=False)


class ImportStatus(Enum):
    STARTED = "Started"
    NOT_STARTED = "Not started"
    UNKNOWN = "Unknown"
    SUCCESS = "Success"
    UNAUTHORIZED = "401 Unauthorized"
    RATE_LIMIT = "429 Rate Limit. Re-queued."
    CONNECTION_ERROR = "Connection error. Re-queued."
    TIMEOUT = "Request timed out. Re-queued."
    UNEXPECTED_ERROR = "Unexpected error. Check logs."
    SKIPPED = "Completed with skipped records. Check logs."
    SERVER_ERROR = "Server error. Re-queued."


def parseRange(range: str) -> int:
    """Parses a range string formatted as '7d', '30d', '6m', '1y' into days."""
    if not range or len(range) < 2:
        raise ValueError("Invalid range string")

    unit = range[-1]
    try:
        value = int(range[:-1])
    except ValueError:
        raise ValueError("Invalid range value")

    if unit == "d":
        days = value
    elif unit == "m":
        days = value * 30
    elif unit == "y":
        days = value * 365
    else:
        raise ValueError("Invalid range unit")

    if days < 0 or days > 3650:
        raise ValueError("Invalid range value")

    return days
