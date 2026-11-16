from datetime import datetime

from src.models.cycle import WhoopCycle


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
