import logging
from collections import defaultdict
from datetime import datetime
from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect as sa_inspect

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
    """Insert new rows and update existing ones, matched by primary key."""
    by_class = defaultdict(list)
    for model in models:
        by_class[type(model)].append(model)

    try:
        for cls, items in by_class.items():
            mapper = sa_inspect(cls)
            pk_column = mapper.primary_key[0]
            pk_attr = mapper.get_property_by_column(pk_column).key
            ids = [getattr(m, pk_attr) for m in items if getattr(m, pk_attr) is not None]

            # Keep a strong reference so merge() finds the rows in the identity map
            # instead of issuing one SELECT per row.
            loaded = []
            for i in range(0, len(ids), _PRELOAD_CHUNK):
                chunk = ids[i : i + _PRELOAD_CHUNK]
                loaded.extend(db.session.query(cls).filter(pk_column.in_(chunk)).all())

            for model in items:
                db.session.merge(model)
        db.session.commit()
    except Exception:
        db.session.rollback()
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
