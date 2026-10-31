import logging
from datetime import datetime
from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

db = SQLAlchemy()


def query_all(model):
    try:
        return db.session.query(model).order_by(model.timestamp.desc()).all()
    except Exception:
        db.session.rollback()
        raise


def query_all_between(model, start: datetime, end: datetime) -> List:
    try:
        return (
            db.session.query(model)
            .filter(model.timestamp.between(start, end))
            .order_by(model.timestamp.desc())
            .all()
        )
    except Exception:
        db.session.rollback()
        raise


def add_all(models):
    """Add a list of models to the database."""
    models = list(models)
    try:
        db.session.add_all(models)
        db.session.commit()
        return
    except IntegrityError:
        db.session.rollback()

    # Fall back to per-row commits so one duplicate/bad row does not discard
    # the whole batch.
    for model in models:
        try:
            db.session.add(model)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        except Exception:
            raise


def _migrate_schema():
    """Best-effort, idempotent migration for columns added after 1.1.1.

    ``db.create_all()`` does not alter existing tables, so users upgrading from
    an older release need these columns added manually otherwise. Running the
    statements here (and ignoring "already exists"/"does not exist" errors)
    keeps upgrades working without a separate migration tool.
    """
    statements_pg = [
        'ALTER TABLE whoop_cycle ADD COLUMN IF NOT EXISTS user_id BIGINT',
        'ALTER TABLE whoop_cycle ADD COLUMN IF NOT EXISTS step_count INTEGER',
        'ALTER TABLE whoop_cycle ALTER COLUMN "end" DROP NOT NULL',
        'ALTER TABLE whoop_sleep ADD COLUMN IF NOT EXISTS user_id BIGINT',
    ]
    statements_mysql = [
        'ALTER TABLE whoop_cycle ADD COLUMN user_id BIGINT NULL',
        'ALTER TABLE whoop_cycle ADD COLUMN step_count INT NULL',
        'ALTER TABLE whoop_cycle MODIFY `end` DATETIME NULL',
        'ALTER TABLE whoop_sleep ADD COLUMN user_id BIGINT NULL',
    ]

    dialect = db.engine.dialect.name
    statements = statements_pg if dialect == "postgresql" else statements_mysql

    for stmt in statements:
        try:
            db.session.execute(db.text(stmt))
            db.session.commit()
        except Exception as exc:  # noqa: BLE001 - best effort
            db.session.rollback()
            logger.debug("Migration statement skipped: %s (%s)", stmt, exc)


def init_app(app):
    """Initializes the database extension."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _migrate_schema()
