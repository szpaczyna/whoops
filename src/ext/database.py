import logging
from collections import defaultdict
from datetime import datetime
from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect as sa_inspect
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


_PRELOAD_CHUNK = 500


def upsert_all(models):
    """Insert new rows and update existing ones, matched by primary key.

    If the batch violates a constraint, rows are retried one by one and the
    offending ones are logged and skipped.
    """
    models = list(models)
    try:
        _merge_batch(models)
        db.session.commit()
        return
    except IntegrityError as exc:
        db.session.rollback()
        logger.warning("Batch upsert failed (%s), retrying row by row", _first_line(exc))
    except Exception:
        db.session.rollback()
        raise

    for model in models:
        try:
            db.session.merge(model)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            logger.warning("Skipped %s %s: %s", type(model).__name__, _pk_of(model), _first_line(exc))
        except Exception:
            db.session.rollback()
            raise


def _merge_batch(models):
    by_class = defaultdict(list)
    for model in models:
        by_class[type(model)].append(model)

    for cls, items in by_class.items():
        pk_column = sa_inspect(cls).primary_key[0]
        ids = [_pk_of(m) for m in items if _pk_of(m) is not None]

        # Keep a strong reference so merge() finds the rows in the identity map
        # instead of issuing one SELECT per row.
        loaded = []
        for i in range(0, len(ids), _PRELOAD_CHUNK):
            chunk = ids[i : i + _PRELOAD_CHUNK]
            loaded.extend(db.session.query(cls).filter(pk_column.in_(chunk)).all())

        for model in items:
            db.session.merge(model)


def _pk_of(model):
    mapper = sa_inspect(type(model))
    return getattr(model, mapper.get_property_by_column(mapper.primary_key[0]).key)


def _first_line(exc: IntegrityError) -> str:
    # The DETAIL line of the driver error echoes the whole row.
    return str(exc.orig).splitlines()[0]


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
        'ALTER TABLE whoop_recovery ALTER COLUMN spo2_perc DROP NOT NULL',
        'ALTER TABLE whoop_recovery ALTER COLUMN skin_temp_celsius DROP NOT NULL',
    ]
    statements_mysql = [
        'ALTER TABLE whoop_cycle ADD COLUMN user_id BIGINT NULL',
        'ALTER TABLE whoop_cycle ADD COLUMN step_count INT NULL',
        'ALTER TABLE whoop_cycle MODIFY `end` DATETIME NULL',
        'ALTER TABLE whoop_sleep ADD COLUMN user_id BIGINT NULL',
        'ALTER TABLE whoop_recovery MODIFY spo2_perc FLOAT NULL',
        'ALTER TABLE whoop_recovery MODIFY skin_temp_celsius FLOAT NULL',
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
