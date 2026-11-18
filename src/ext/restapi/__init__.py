from flask import Blueprint
from flask_restful import Api

from src.models import WhoopCycle, WhoopRecovery, WhoopSleep, WhoopWorkout

from .resources import (
    ModelDataResource,
    UserBodyMeasurementResource,
    UserProfileResource,
)


def init_app(app):
    bp = Blueprint("restapi", __name__, url_prefix="/api/v1")
    api = Api(bp)
    for path, endpoint, model in (
        ("/whoop/cycle", "cycle", WhoopCycle),
        ("/whoop/recovery", "recovery", WhoopRecovery),
        ("/whoop/activity/sleep", "sleep", WhoopSleep),
        ("/whoop/activity/workout", "workout", WhoopWorkout),
    ):
        api.add_resource(ModelDataResource, path, endpoint=endpoint, resource_class_kwargs={"model": model})
    api.add_resource(UserProfileResource, "/whoop/user/profile")
    api.add_resource(UserBodyMeasurementResource, "/whoop/user/body")
    app.register_blueprint(bp)
