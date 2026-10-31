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