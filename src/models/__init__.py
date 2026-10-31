from typing import TypeVar

from .cycle import WhoopCycle
from .recovery import WhoopRecovery
from .sleep import WhoopSleep
from .workout import WhoopWorkout

Model = TypeVar("Model", WhoopCycle, WhoopRecovery, WhoopSleep, WhoopWorkout)


_MODEL_BY_ROUTE = {
    "whoop/cycle": WhoopCycle,
    "whoop/recovery": WhoopRecovery,
    "whoop/activity/sleep": WhoopSleep,
    "whoop/activity/workout": WhoopWorkout,
}


def from_path(path: str):
    normalized = path.rstrip("/")
    for route, model in _MODEL_BY_ROUTE.items():
        if normalized.endswith(route):
            return model
    raise ValueError(f"Unknown model for path: {path}")
