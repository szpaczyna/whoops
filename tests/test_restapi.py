from unittest.mock import patch

import pytest
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
def client():
    app = Flask(__name__)
    restapi.init_app(app)
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
