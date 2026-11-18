import requests
from flask import abort, current_app, jsonify
from flask_restful import Resource

from src.ext.restapi.utils import records_from_request


def _abort_whoop_error(exc: requests.HTTPError):
    abort(exc.response.status_code, description=str(exc))


class ModelDataResource(Resource):
    def __init__(self, model):
        self.model = model

    def get(self):
        return records_from_request(self.model)


class UserProfileResource(Resource):
    def get(self):
        whoop_client = current_app.config["WhoopClient"]
        try:
            return jsonify(whoop_client.get_profile_basic())
        except requests.HTTPError as e:
            _abort_whoop_error(e)


class UserBodyMeasurementResource(Resource):
    def get(self):
        whoop_client = current_app.config["WhoopClient"]
        try:
            return jsonify(whoop_client.get_body_measurement())
        except requests.HTTPError as e:
            _abort_whoop_error(e)
