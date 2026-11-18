from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask

from src.ext import restapi
from src.models import WhoopCycle, WhoopRecovery, WhoopSleep, WhoopWorkout

ROUTES = [
    ("/api/v1/whoop/cycle", WhoopCycle),
    ("/api/v1/whoop/recovery", WhoopRecovery),
    ("/api/v1/whoop/activity/sleep", WhoopSleep),
    ("/api/v1/whoop/activity/workout", WhoopWorkout),
]


@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    restapi.init_app(app)
    return app


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.mark.parametrize("path,model", ROUTES)
def test_records_without_range(client, path, model):
    with patch("src.ext.restapi.utils.query_all", return_value=[]) as query_all:
        resp = client.get(path)

    assert resp.status_code == 200
    assert resp.get_json() == {"records": []}
    query_all.assert_called_once_with(model)


@pytest.mark.parametrize("path,model", ROUTES)
def test_records_with_range(client, path, model):
    with patch(
        "src.ext.restapi.utils.query_all_between", return_value=[]
    ) as query_all_between:
        resp = client.get(path, query_string={"range": "3d"})

    assert resp.status_code == 200
    assert resp.get_json() == {"records": []}
    query_all_between.assert_called_once()
    assert query_all_between.call_args.args[0] is model


def test_invalid_range(client):
    resp = client.get("/api/v1/whoop/cycle", query_string={"range": "xd"})

    assert resp.status_code == 400


def test_profile_json_error(app):
    mock_client = MagicMock()
    mock_client.get_profile_basic.side_effect = requests.HTTPError(
        "401 Unauthorized", response=MagicMock(status_code=401)
    )
    app.config["WhoopClient"] = mock_client
    client = app.test_client()

    resp = client.get("/api/v1/whoop/user/profile")

    assert resp.status_code == 401
    assert resp.mimetype == "application/json"
    assert isinstance(resp.get_json()["message"], str)


def test_range_seven_days(client):
    with patch(
        "src.ext.restapi.utils.query_all_between", return_value=[]
    ) as query_all_between:
        client.get("/api/v1/whoop/cycle", query_string={"range": "7d"})

    start = query_all_between.call_args.args[1]
    delta = datetime.now(timezone.utc) - start
    assert abs(delta.total_seconds() - 7 * 86400) <= 2
