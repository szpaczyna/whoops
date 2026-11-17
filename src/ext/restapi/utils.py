import logging
from datetime import datetime, timedelta, timezone

from flask import request

from src.ext.database import query_all, query_all_between
from src.utils import parseRange

logger = logging.getLogger(__name__)


def records_from_request(model):
    args = request.args.to_dict()
    range = args.get("range")

    if not range:
        records = query_all(model)
        return {"records": [r.to_dict() for r in records]}, 200

    try:
        range = parseRange(range)
    except ValueError as e:
        return {"message": str(e)}, 400

    now = datetime.now(tz=timezone.utc)
    start = now - timedelta(days=range + 1)

    records = query_all_between(model, start, now)

    return {"records": [r.to_dict() for r in records]}, 200
