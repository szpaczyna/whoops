import json
from datetime import datetime

from src.ext.database import db


class WhoopToken(db.Model):
    """Persisted Whoop OAuth tokens (single row)."""

    __tablename__ = "whoop_token"

    id = db.Column(db.Integer, primary_key=True)
    tokens_json = db.Column(db.Text, nullable=False)
    refreshed_at = db.Column(db.DateTime(timezone=True), nullable=False)


def save_tokens(client) -> None:
    """Upsert the client's tokens into the database."""
    row = WhoopToken.query.first()
    if row is None:
        row = WhoopToken()
    row.tokens_json = json.dumps(client.tokens)
    row.refreshed_at = client.refreshed_at
    db.session.add(row)
    db.session.commit()


def load_tokens(client) -> bool:
    """Load persisted tokens into the client. Returns True if loaded."""
    row = WhoopToken.query.first()
    if row is None:
        return False
    try:
        client.tokens = json.loads(row.tokens_json)
        client.refreshed_at = row.refreshed_at
    except (ValueError, TypeError):
        return False
    return True