from datetime import datetime, timezone

import pytest
from flask import Flask

from src.ext.database import db
from src.models.token import load_tokens, save_tokens
from src.whoop import WhoopClient


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()


def test_tokens_survive_a_restart(app):
    tokens = {"access_token": "access", "refresh_token": "refresh"}
    client = WhoopClient("id", "secret")
    client.tokens = tokens
    client.refreshed_at = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)

    with app.app_context():
        save_tokens(client)

    restarted = WhoopClient("id", "secret")
    with app.app_context():
        assert load_tokens(restarted) is True

    assert restarted.tokens == tokens
