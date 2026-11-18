import logging

import pytest
from sqlalchemy import event

from src.ext.database import _migrate_schema, db, upsert_all


class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


class Record(db.Model):
    __tablename__ = "record"
    id = db.Column(db.String(36), primary_key=True)
    score_state = db.Column(db.String(15), nullable=True)


@pytest.fixture
def app():
    app = __import__("flask").Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
    yield app


def _select_counter():
    statements = []

    def _count(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    return statements, _count


def test_upsert_all_commits_all_rows(app):
    with app.app_context():
        assert upsert_all([Item(name="a"), Item(name="b")]) == 0
        assert db.session.query(Item).count() == 2


def test_upsert_all_is_idempotent(app):
    with app.app_context():
        upsert_all([Record(id="1", score_state="SCORED")])
        upsert_all([Record(id="1", score_state="SCORED")])
        assert db.session.query(Record).count() == 1


def test_upsert_all_updates_existing_rows(app):
    with app.app_context():
        upsert_all([Record(id="1", score_state="PENDING_SCORE")])
        upsert_all([Record(id="1", score_state="SCORED")])
        db.session.expire_all()
        assert db.session.get(Record, "1").score_state == "SCORED"


def test_upsert_all_mixed_batch(app):
    with app.app_context():
        upsert_all([Record(id="1", score_state="PENDING_SCORE")])
        upsert_all([Record(id="1", score_state="SCORED"), Record(id="2", score_state="SCORED")])
        db.session.expire_all()
        rows = {r.id: r.score_state for r in db.session.query(Record).all()}
        assert rows == {"1": "SCORED", "2": "SCORED"}


def test_upsert_all_duplicate_ids_in_one_batch(app):
    with app.app_context():
        upsert_all([Record(id="1", score_state="PENDING_SCORE"), Record(id="1", score_state="SCORED")])
        db.session.expire_all()
        assert db.session.get(Record, "1").score_state == "SCORED"


def test_upsert_all_preloads_existing_rows_in_one_select(app):
    with app.app_context():
        upsert_all([Record(id=str(i)) for i in range(50)])
        db.session.expire_all()

        statements, counter = _select_counter()
        event.listen(db.engine, "before_cursor_execute", counter)
        try:
            upsert_all([Record(id=str(i), score_state="SCORED") for i in range(50)])
        finally:
            event.remove(db.engine, "before_cursor_execute", counter)

        assert len(statements) == 1


def test_upsert_all_rolls_back_and_raises(app, monkeypatch):
    with app.app_context():
        upsert_all([Item(name="a")])
        monkeypatch.setattr(db.session, "merge", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
        with pytest.raises(RuntimeError):
            upsert_all([Item(name="b")])
        monkeypatch.undo()
        assert db.session.query(Item).count() == 1


def test_upsert_all_skips_rows_that_violate_constraints(app, caplog):
    with app.app_context():
        upsert_all([Item(name="a")])
        assert upsert_all([Item(name="b"), Item(name="a"), Item(name="c")]) == 1
        assert sorted(i.name for i in db.session.query(Item).all()) == ["a", "b", "c"]
    assert "Skipped Item" in caplog.text


def test_upsert_all_null_in_not_null_column_keeps_other_rows(app, caplog):
    with app.app_context():
        assert upsert_all([Record(id="1"), Item(name=None), Record(id="2")]) == 1
        assert db.session.query(Record).count() == 2
        assert db.session.query(Item).count() == 0
    assert "Skipped Item" in caplog.text


def test_migrate_schema_logs_skipped_statements_at_info(app, caplog):
    caplog.set_level(logging.INFO, logger="src.ext.database")
    with app.app_context():
        _migrate_schema()
    assert any(
        r.levelno == logging.INFO and "Migration statement skipped" in r.getMessage() for r in caplog.records
    )
