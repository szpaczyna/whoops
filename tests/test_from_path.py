from src.models import from_path, WhoopCycle, WhoopRecovery, WhoopSleep, WhoopWorkout


def test_from_path_mapping():
    assert from_path("/api/v1/whoop/cycle") is WhoopCycle
    assert from_path("/api/v1/whoop/recovery") is WhoopRecovery
    assert from_path("/api/v1/whoop/activity/sleep") is WhoopSleep
    assert from_path("/api/v1/whoop/activity/workout") is WhoopWorkout


def test_from_path_unknown():
    import pytest

    with pytest.raises(ValueError):
        from_path("/api/v1/whoop/unknown")