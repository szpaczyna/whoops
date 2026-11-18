from datetime import datetime

from src.models.cycle import WhoopCycle
from src.models.sleep import WhoopSleep
from src.models.recovery import WhoopRecovery
from src.models.workout import WhoopWorkout


def test_active_cycle_without_end():
    data = {
        "id": 1,
        "created_at": "2026-10-31T10:00:00Z",
        "updated_at": "2026-10-31T10:00:00Z",
        "start": "2026-10-31T09:00:00Z",
        "end": None,
        "timezone_offset": "Z",
        "score_state": "PENDING_SCORE",
        "score": {"strain": 0, "kilojoule": 0, "average_heart_rate": 0, "max_heart_rate": 0},
    }
    cycle = WhoopCycle.from_json(data)
    assert cycle.id == 1
    assert cycle.end is None
    assert cycle.score_state == "PENDING_SCORE"


def test_recovery_without_spo2_and_skin_temp():
    from src.models.recovery import WhoopRecovery

    data = {
        "sleep_id": "7e6ed812-e80d-4bbf-9f7a-9fd19a84e47e",
        "cycle_id": 1900645906,
        "user_id": 29791235,
        "created_at": "2026-10-25T03:25:37.286Z",
        "updated_at": "2026-10-25T06:10:27.431Z",
        "score_state": "SCORED",
        "score": {
            "user_calibrating": False,
            "recovery_score": 99,
            "resting_heart_rate": 62,
            "hrv_rmssd_milli": 48.06833,
            "spo2_percentage": None,
        },
    }
    recovery = WhoopRecovery.from_json(data)
    assert recovery.spo2_perc is None
    assert recovery.skin_temp_celsius is None


def test_sleep_with_null_score_and_missing_updated_at():
    data = {
        "id": "sleep-1",
        "cycle_id": 1,
        "created_at": "2026-10-31T10:00:00Z",
        "start": "2026-10-31T09:00:00Z",
        "end": "2026-10-31T10:00:00Z",
        "score": None,
    }
    sleep = WhoopSleep.from_json(data)
    assert sleep.respiratory_rate is None
    assert sleep.performance_perc is None
    assert sleep.consistency_perc is None
    assert sleep.efficiency_perc is None
    assert sleep.total_in_bed_ms is None
    assert sleep.updated_at is None


def test_sleep_with_null_stage_summary_and_sleep_needed():
    data = {
        "id": "sleep-2",
        "cycle_id": 1,
        "created_at": "2026-10-31T10:00:00Z",
        "start": "2026-10-31T09:00:00Z",
        "end": "2026-10-31T10:00:00Z",
        "score": {"stage_summary": None, "sleep_needed": None},
    }
    sleep = WhoopSleep.from_json(data)
    assert sleep.total_in_bed_ms is None
    assert sleep.total_awake_ms is None
    assert sleep.sleep_needed_baseline_ms is None
    assert sleep.sleep_debt_ms is None


def test_cycle_missing_updated_at_falls_back_to_created_at():
    data = {
        "id": 1,
        "created_at": "2026-10-31T10:00:00Z",
        "start": "2026-10-31T09:00:00Z",
        "end": "2026-10-31T10:00:00Z",
        "timezone_offset": "Z",
        "score_state": "SCORED",
        "score": {"strain": 0, "kilojoule": 0, "average_heart_rate": 0, "max_heart_rate": 0},
    }
    cycle = WhoopCycle.from_json(data)
    assert cycle.updated_at == cycle.timestamp


def test_recovery_missing_updated_at_falls_back_to_created_at():
    data = {
        "sleep_id": "7e6ed812-e80d-4bbf-9f7a-9fd19a84e47e",
        "cycle_id": 1900645906,
        "user_id": 29791235,
        "created_at": "2026-10-25T03:25:37.286Z",
        "score_state": "SCORED",
        "score": {
            "user_calibrating": False,
            "recovery_score": 99,
            "resting_heart_rate": 62,
            "hrv_rmssd_milli": 48.06833,
        },
    }
    recovery = WhoopRecovery.from_json(data)
    assert recovery.updated_at == recovery.timestamp


def test_workout_missing_sport_name_is_none():
    data = {
        "id": "workout-1",
        "created_at": "2026-10-31T10:00:00Z",
        "start": "2026-10-31T09:00:00Z",
        "end": "2026-10-31T10:00:00Z",
    }
    workout = WhoopWorkout.from_json(data)
    assert workout.sport_name is None
