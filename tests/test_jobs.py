from collections import deque
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from src.ext import jobs
from src.ext.database import db
from src.ext.webui import bp
from src.models.schedule import load_schedule, save_schedule
from src.models.workout import WhoopWorkout
from src.utils import ImportStatus, ImportTask


class FakeClient:
    def __init__(self):
        self.tokens = {"access_token": "tok", "refresh_token": "ref"}
        self.refresh_token = MagicMock()

    def get_workouts(self, start=None):
        return []

    def get_cycles(self, start=None):
        return []

    def get_sleeps(self, start=None):
        return []

    def get_recoveries(self, start=None):
        return []


def _http_error(status_code):
    response = MagicMock(status_code=status_code)
    return requests.HTTPError(f"{status_code}", response=response)


def _workout(workout_id):
    return WhoopWorkout.from_json({
        "id": workout_id,
        "created_at": "2026-11-15T10:00:00Z",
        "updated_at": "2026-11-15T10:00:00Z",
        "start": "2026-11-15T09:00:00Z",
        "end": "2026-11-15T09:30:00Z",
        "sport_name": "walking",
        "score_state": "SCORED",
        "score": {"strain": 5.0},
    })


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["ImportQueue"] = deque()
    app.config["WhoopClient"] = FakeClient()
    db.init_app(app)
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
    yield app
    scheduler = app.config.get("Scheduler")
    if isinstance(scheduler, BackgroundScheduler) and scheduler.running:
        scheduler.shutdown(wait=False)


@pytest.fixture
def paused_scheduler(app):
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.start(paused=True)
    app.config["Scheduler"] = scheduler
    return scheduler


def test_fill_backlog_queues_full_import(app):
    app.config["Scheduler"] = MagicMock()
    jobs.fill_backlog(app)
    queue = app.config["ImportQueue"]
    assert len(queue) == 4
    assert all(task.start is None for task in queue)


def test_fill_backlog_deduplicates(app):
    app.config["Scheduler"] = MagicMock()
    jobs.fill_backlog(app)
    jobs.fill_backlog(app)
    assert len(app.config["ImportQueue"]) == 4


def test_incremental_backlog_uses_configured_window(app):
    app.config["Scheduler"] = MagicMock()
    jobs.incremental_backlog(app)
    expected = datetime.now(timezone.utc) - timedelta(days=7)
    for task in app.config["ImportQueue"]:
        assert abs(task.start - expected) < timedelta(seconds=5)


def test_worker_passes_start_and_upserts(app):
    start = datetime(2026, 11, 9, tzinfo=timezone.utc)
    fetch = MagicMock(return_value=[_workout("w1")])
    app.config["ImportQueue"].append(ImportTask(WhoopWorkout, fetch, start))

    jobs._import_worker(app)
    app.config["ImportQueue"].append(ImportTask(WhoopWorkout, fetch, start))
    jobs._import_worker(app)

    fetch.assert_called_with(start=start)
    assert app.config["LastImportStatus"] == ImportStatus.SUCCESS
    with app.app_context():
        assert db.session.query(WhoopWorkout).count() == 1


def test_worker_401_refreshes_and_requeues(app):
    fetch = MagicMock(side_effect=_http_error(401))
    other = ImportTask(WhoopWorkout, FakeClient().get_cycles)
    queue = app.config["ImportQueue"]
    queue.extend([ImportTask(WhoopWorkout, fetch), other])

    jobs._import_worker(app)

    app.config["WhoopClient"].refresh_token.assert_called_once()
    assert len(queue) == 2
    assert queue[0].callable is fetch
    assert queue[0].retried_after_401 is True
    assert app.config["LastImportStatus"] == ImportStatus.STARTED


def test_worker_401_with_failed_refresh_clears_queue(app):
    app.config["WhoopClient"].refresh_token.side_effect = _http_error(401)
    queue = app.config["ImportQueue"]
    queue.extend([ImportTask(WhoopWorkout, MagicMock(side_effect=_http_error(401))),
                  ImportTask(WhoopWorkout, FakeClient().get_cycles)])

    jobs._import_worker(app)

    assert len(queue) == 0
    assert app.config["LastImportStatus"] == ImportStatus.UNAUTHORIZED


def test_worker_second_401_gives_up(app):
    queue = app.config["ImportQueue"]
    queue.append(ImportTask(WhoopWorkout, MagicMock(side_effect=_http_error(401)), retried_after_401=True))

    jobs._import_worker(app)

    app.config["WhoopClient"].refresh_token.assert_not_called()
    assert len(queue) == 0
    assert app.config["LastImportStatus"] == ImportStatus.UNAUTHORIZED


def test_schedule_save_load_overwrite(app):
    with app.app_context():
        assert load_schedule() is None
        save_schedule(7, 30)
        save_schedule(8, 15)
        assert load_schedule() == (8, 15)


def test_init_app_restores_saved_schedule(app):
    with app.app_context():
        save_schedule(7, 30)
    jobs.init_app(app)
    job = app.config["Scheduler"].get_job(jobs.IMPORT_JOB_ID)
    assert job is not None
    assert job.func is jobs.incremental_backlog
    assert str(job.trigger.fields[5]) == "7"
    assert str(job.trigger.fields[6]) == "30"


def test_init_app_without_schedule_has_no_import_job(app):
    jobs.init_app(app)
    assert app.config["Scheduler"].get_job(jobs.IMPORT_JOB_ID) is None


def test_post_schedule_persists_and_registers(app, paused_scheduler):
    response = app.test_client().post("/schedule", json={"hour": 7, "minute": 30})
    assert response.status_code == 201
    assert paused_scheduler.get_job(jobs.IMPORT_JOB_ID) is not None
    with app.app_context():
        assert load_schedule() == (7, 30)


def test_post_schedule_rejects_invalid_input(app, paused_scheduler):
    response = app.test_client().post("/schedule", json={"hour": 25, "minute": 0})
    assert response.status_code == 400
    with app.app_context():
        assert load_schedule() is None


def test_status_reports_schedule(app, paused_scheduler):
    client = app.test_client()
    assert client.get("/import/status").get_json()["schedule"] is None
    client.post("/schedule", json={"hour": 7, "minute": 30})
    assert client.get("/import/status").get_json()["schedule"] == {"hour": 7, "minute": 30}


def test_delete_schedule_removes_row_and_job_idempotently(app, paused_scheduler):
    client = app.test_client()
    client.post("/schedule", json={"hour": 7, "minute": 30})

    assert client.delete("/schedule").status_code == 200
    assert client.delete("/schedule").status_code == 200

    assert paused_scheduler.get_job(jobs.IMPORT_JOB_ID) is None
    with app.app_context():
        assert load_schedule() is None
