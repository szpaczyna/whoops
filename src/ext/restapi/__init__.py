from flask import Blueprint
from flask_restful import Api

from .resources import (
    CycleDataResource,
    RecoveryDataResource,
    SleepDataResource,
    UserBodyMeasurementResource,
    UserProfileResource,
    WhoopDataResource,
    WorkoutDataResource,
)

bp = Blueprint("restapi", __name__, url_prefix="/api/v1")
api = Api(bp)


def init_app(app):
    api.add_resource(WhoopDataResource, "/whoop/data")
    api.add_resource(CycleDataResource, "/whoop/cycle")
    api.add_resource(RecoveryDataResource, "/whoop/recovery")
    api.add_resource(SleepDataResource, "/whoop/activity/sleep")
    api.add_resource(WorkoutDataResource, "/whoop/activity/workout")
    api.add_resource(UserProfileResource, "/whoop/user/profile")
    api.add_resource(UserBodyMeasurementResource, "/whoop/user/body")
    app.register_blueprint(bp)
