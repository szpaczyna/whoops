from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from src.ext.webui import bp
from src.whoop import WhoopClient


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test"
    app.config["WhoopClient"] = MagicMock()
    app.register_blueprint(bp)
    with patch("src.models.token.save_tokens"):
        yield app


def test_callback_without_prior_state_redirects(app):
    response = app.test_client().get("/callback?state=x&code=c")

    assert response.status_code == 302
    app.config["WhoopClient"].set_tokens.assert_not_called()


def test_callback_state_is_single_use(app):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["oauth_state"] = "abc"

    client.get("/callback?state=abc&code=c")
    client.get("/callback?state=abc&code=c")

    app.config["WhoopClient"].set_tokens.assert_called_once_with("c")


def test_authorize_stores_oauth_state_in_session(app):
    app.config["WhoopClient"] = WhoopClient("id", "secret")
    app.config["REDIRECT_URI"] = "http://localhost/cb"
    client = app.test_client()

    response = client.get("/authorize")

    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert "oauth_state" in sess
