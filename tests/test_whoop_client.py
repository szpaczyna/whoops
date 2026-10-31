from unittest.mock import patch, MagicMock

from src.whoop import WhoopClient


def test_authorization_url_scopes():
    client = WhoopClient("id", "secret")
    # avoid Flask current_app dependency by monkeypatching config access
    import src.whoop as w
    # Provide a fake current_app
    fake_app = MagicMock()
    fake_app.config = {"REDIRECT_URI": "http://localhost/cb", "OAuthState": None}
    with patch.object(w, "current_app", fake_app):
        url = client.authorization_url()
    assert "read%3Aprofile" in url
    assert "read%3Abody_measurement" in url
    assert "read%3Acycles" in url


def test_get_profile_basic_url():
    client = WhoopClient("id", "secret")
    client.tokens = {"access_token": "tok"}
    with patch("src.whoop.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"user_id": 1, "email": "a@b.com", "first_name": "A", "last_name": "B"})
        mock_get.return_value.raise_for_status = MagicMock()
        result = client.get_profile_basic()
    assert result["email"] == "a@b.com"
    called_url = mock_get.call_args.args[0]
    assert called_url.endswith("developer/v2/user/profile/basic")