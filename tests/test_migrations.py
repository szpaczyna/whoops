import os

import pytest
from flask import Flask
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
)

from src.ext.database import _migrate_schema, db

SLEEP_NOT_NULL_COLUMNS = [
    "respiratory_rate",
    "performance_perc",
    "consistency_perc",
    "efficiency_perc",
    "total_in_bed_ms",
    "total_awake_ms",
    "total_light_sleep_ms",
    "total_slow_wave_sleep_ms",
    "total_rem_sleep_ms",
    "sleep_cycle_count",
    "disturbance_count",
    "sleep_needed_baseline_ms",
    "sleep_debt_ms",
    "add_sleep_from_strain_ms",
]


def _build_old_metadata():
    metadata = MetaData()

    Table(
        "whoop_cycle",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("timestamp", DateTime(timezone=True), nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=False),
        Column("start", DateTime(timezone=True), nullable=False),
        Column("end", DateTime(timezone=True), nullable=False),
        Column("timezone_offset", String(10), nullable=False),
        Column("score_state", String(15), nullable=False),
        Column("strain", Float, nullable=False),
        Column("kilojoule", Float, nullable=False),
        Column("avg_heart_rate", Integer, nullable=False),
        Column("max_heart_rate", Integer, nullable=False),
    )

    Table(
        "whoop_sleep",
        metadata,
        Column("id", String(36), primary_key=True),
        Column("cycle_id", BigInteger, nullable=False),
        Column("timestamp", DateTime(timezone=True), nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=True),
        Column("start", DateTime(timezone=True), nullable=False),
        Column("end", DateTime(timezone=True), nullable=False),
        Column("timezone_offset", String(10), nullable=True),
        Column("nap", Boolean, nullable=True),
        Column("score_state", String(15), nullable=True),
        Column("respiratory_rate", Float, nullable=False),
        Column("performance_perc", Integer, nullable=False),
        Column("consistency_perc", Integer, nullable=False),
        Column("efficiency_perc", Integer, nullable=False),
        Column("total_in_bed_ms", BigInteger, nullable=False),
        Column("total_awake_ms", BigInteger, nullable=False),
        Column("total_no_data_ms", BigInteger, nullable=True),
        Column("total_light_sleep_ms", BigInteger, nullable=False),
        Column("total_slow_wave_sleep_ms", BigInteger, nullable=False),
        Column("total_rem_sleep_ms", BigInteger, nullable=False),
        Column("sleep_cycle_count", Integer, nullable=False),
        Column("disturbance_count", Integer, nullable=False),
        Column("sleep_needed_baseline_ms", BigInteger, nullable=False),
        Column("sleep_debt_ms", BigInteger, nullable=False),
        Column("add_sleep_from_strain_ms", BigInteger, nullable=False),
        Column("add_sleep_from_nap_ms", BigInteger, nullable=True),
    )

    Table(
        "whoop_recovery",
        metadata,
        Column("sleep_id", String(36), primary_key=True),
        Column("cycle_id", BigInteger, nullable=False),
        Column("user_id", BigInteger, nullable=False),
        Column("timestamp", DateTime(timezone=True), nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=False),
        Column("score_state", String(15), nullable=False),
        Column("user_calibrating", Boolean, nullable=False),
        Column("recovery_score", Integer, nullable=False),
        Column("resting_heart_rate", Integer, nullable=False),
        Column("hrv_rmssd_ms", Float, nullable=False),
        Column("spo2_perc", Float, nullable=False),
        Column("skin_temp_celsius", Float, nullable=False),
    )

    Table(
        "whoop_workout",
        metadata,
        Column("id", String(36), primary_key=True),
        Column("user_id", Integer, nullable=True),
        Column("timestamp", DateTime(timezone=True), nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=True),
        Column("start", DateTime(timezone=True), nullable=False),
        Column("end", DateTime(timezone=True), nullable=False),
        Column("timezone_offset", String(10), nullable=True),
        Column("sport_name", String(32), nullable=False),
        Column("score_state", String(15), nullable=True),
        Column("strain", Float, nullable=True),
        Column("avg_heart_rate", Integer, nullable=True),
        Column("max_heart_rate", Integer, nullable=True),
        Column("kilojoule", Float, nullable=True),
        Column("percent_recorded", Float, nullable=True),
        Column("distance_meter", Float, nullable=True),
        Column("altitude_gain_meter", Float, nullable=True),
        Column("altitude_change_meter", Float, nullable=True),
        Column("zone_zero_milli", Integer, nullable=True),
        Column("zone_one_milli", Integer, nullable=True),
        Column("zone_two_milli", Integer, nullable=True),
        Column("zone_three_milli", Integer, nullable=True),
        Column("zone_four_milli", Integer, nullable=True),
        Column("zone_five_milli", Integer, nullable=True),
    )

    return metadata


def _column_map(inspector, table_name):
    return {c["name"]: c for c in inspector.get_columns(table_name)}


@pytest.mark.parametrize("env_var", ["TEST_POSTGRES_URI", "TEST_MYSQL_URI"])
def test_migrate_schema(env_var):
    uri = os.getenv(env_var)
    if not uri:
        pytest.skip(f"{env_var} not set")

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    metadata = _build_old_metadata()
    with app.app_context():
        try:
            metadata.drop_all(bind=db.engine, checkfirst=True)
            metadata.create_all(bind=db.engine)
            _migrate_schema()

            from sqlalchemy import inspect as sa_inspect

            inspector = sa_inspect(db.engine)

            cycle_cols = _column_map(inspector, "whoop_cycle")
            assert "user_id" in cycle_cols
            assert "step_count" in cycle_cols
            assert cycle_cols["end"]["nullable"] is True

            sleep_cols = _column_map(inspector, "whoop_sleep")
            assert "user_id" in sleep_cols
            for name in SLEEP_NOT_NULL_COLUMNS:
                assert sleep_cols[name]["nullable"] is True, name

            recovery_cols = _column_map(inspector, "whoop_recovery")
            assert recovery_cols["spo2_perc"]["nullable"] is True
            assert recovery_cols["skin_temp_celsius"]["nullable"] is True

            workout_cols = _column_map(inspector, "whoop_workout")
            assert workout_cols["sport_name"]["nullable"] is True
        finally:
            metadata.drop_all(bind=db.engine, checkfirst=True)
