import pytest
from flask import Flask
from flask_bootstrap import Bootstrap

from src.ext.database import db
from src.ext.webui import bp
from src.models.workout import WhoopWorkout


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    Bootstrap(app)
    db.init_app(app)
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
    yield app


def _add_workout(app):
    with app.app_context():
        db.session.add(WhoopWorkout.from_json({
            "id": 1,
            "created_at": "2026-11-15T10:00:00Z",
            "updated_at": "2026-11-15T10:00:00Z",
            "start": "2026-11-15T09:00:00Z",
            "end": "2026-11-15T09:30:00Z",
            "sport_name": "walking",
            "score_state": "SCORED",
            "score": {"strain": 5.0},
        }))
        db.session.commit()


def test_index_renders_counts(app):
    _add_workout(app)
    response = app.test_client().get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('badge-pill">0</span>') == 3
    assert html.count('badge-pill">1</span>') == 1

