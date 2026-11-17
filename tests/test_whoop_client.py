from unittest.mock import patch, MagicMock

from src.whoop import HTTP_TIMEOUT, WhoopClient


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


def test_get_passes_timeout():
    client = WhoopClient("id", "secret")
    client.tokens = {"access_token": "tok"}
    with patch("src.whoop.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {})
        mock_get.return_value.raise_for_status = MagicMock()
        client.get_profile_basic()
    assert mock_get.call_args.kwargs["timeout"] == HTTP_TIMEOUT


def test_token_request_passes_timeout():
    client = WhoopClient("id", "secret")
    with patch("src.whoop.requests.post") as mock_post:
        mock_post.return_value = MagicMock(json=lambda: {"access_token": "tok"})
        mock_post.return_value.raise_for_status = MagicMock()
        client._post_token_request({})
    assert mock_post.call_args.kwargs["timeout"] == HTTP_TIMEOUT


import threading
import time
from datetime import datetime, timedelta, timezone

import pytest


def _page(records, next_token=None):
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {"records": records, "next_token": next_token}
    return response


def _fresh_client(**kwargs):
    client = WhoopClient("id", "secret", **kwargs)
    client.tokens = {"access_token": "tok", "refresh_token": "ref", "expires_in": 3600}
    client.refreshed_at = datetime.now(timezone.utc)
    return client


def test_fetch_paginated_sends_limit_without_start():
    client = _fresh_client()
    with patch("src.whoop.requests.get", return_value=_page([])) as mock_get:
        client.get_workouts()
    params = mock_get.call_args.kwargs["params"]
    assert params == {"limit": 25}
    assert mock_get.call_args.kwargs["timeout"] == HTTP_TIMEOUT


def test_fetch_paginated_sends_start_on_every_page():
    client = _fresh_client()
    start = datetime(2026, 11, 9, tzinfo=timezone.utc)
    pages = [_page([], next_token="abc"), _page([])]
    with patch("src.whoop.requests.get", side_effect=pages) as mock_get:
        client.get_workouts(start=start)

    assert mock_get.call_count == 2
    first, second = (c.kwargs["params"] for c in mock_get.call_args_list)
    assert first == {"limit": 25, "start": "2026-11-09T00:00:00.000Z"}
    assert second == {"limit": 25, "start": "2026-11-09T00:00:00.000Z", "nextToken": "abc"}


def test_needs_refresh_uses_expires_in_with_margin():
    client = _fresh_client()
    client.refreshed_at = datetime.now(timezone.utc) - timedelta(minutes=45)
    assert client.needs_refresh() is False
    client.refreshed_at = datetime.now(timezone.utc) - timedelta(minutes=51)
    assert client.needs_refresh() is True


def test_needs_refresh_defaults_expires_in():
    client = _fresh_client()
    del client.tokens["expires_in"]
    client.refreshed_at = datetime.now(timezone.utc) - timedelta(minutes=51)
    assert client.needs_refresh() is True


def test_needs_refresh_accepts_naive_refreshed_at():
    client = _fresh_client()
    client.refreshed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    assert client.needs_refresh() is False


def test_concurrent_ensure_fresh_token_refreshes_once():
    client = _fresh_client()
    client.refreshed_at = datetime.now(timezone.utc) - timedelta(hours=2)
    calls = []

    def slow_token_request(params):
        calls.append(params)
        time.sleep(0.1)
        return {"access_token": "new", "refresh_token": "ref2", "expires_in": 3600}

    with patch.object(client, "_post_token_request", side_effect=slow_token_request):
        threads = [threading.Thread(target=client.ensure_fresh_token) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    assert len(calls) == 1
    assert client.tokens["access_token"] == "new"


def test_fetch_paginated_refreshes_between_pages():
    client = _fresh_client()
    new_tokens = {"access_token": "new", "refresh_token": "ref2", "expires_in": 3600}
    pages = [_page([], next_token="abc"), _page([])]

    def get_and_age_token(*args, **kwargs):
        client.refreshed_at = datetime.now(timezone.utc) - timedelta(hours=2)
        return pages.pop(0)

    with patch("src.whoop.requests.get", side_effect=get_and_age_token) as mock_get, \
            patch.object(client, "_post_token_request", return_value=new_tokens):
        client.get_sleeps()

    headers = [c.kwargs["headers"]["Authorization"] for c in mock_get.call_args_list]
    assert headers == ["Bearer tok", "Bearer new"]


def test_refresh_calls_on_refresh_callback():
    seen = []
    client = _fresh_client(on_refresh=seen.append)
    with patch.object(client, "_post_token_request", return_value={"access_token": "new", "expires_in": 3600}):
        client.refresh_token()
    assert seen == [client]


def test_ensure_fresh_token_without_tokens_does_nothing():
    client = WhoopClient("id", "secret")
    with patch.object(client, "_post_token_request") as post:
        assert client.ensure_fresh_token() is False
    post.assert_not_called()


def test_refresh_failure_propagates():
    import requests

    client = _fresh_client()
    client.refreshed_at = datetime.now(timezone.utc) - timedelta(hours=2)
    with patch.object(client, "_post_token_request", side_effect=requests.HTTPError("401")):
        with pytest.raises(requests.HTTPError):
            client.ensure_fresh_token()
