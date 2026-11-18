import requests
from flask import abort, current_app, jsonify
from flask_restful import Resource

from src.ext.restapi.utils import records_from_request


class ModelDataResource(Resource):
    def __init__(self, model):
        self.model = model

    def get(self):
        return records_from_request(self.model)


class WhoopDataResource(Resource):
    def get(self):
        whoop_client = current_app.config["WhoopClient"]

        try:
            cycles = [c.to_dict() for c in whoop_client.get_cycles()[0]]
            sleeps = [s.to_dict() for s in whoop_client.get_sleeps()[0]]
            recoveries = [r.to_dict() for r in whoop_client.get_recoveries()[0]]
            workouts = [w.to_dict() for w in whoop_client.get_workouts()[0]]

            data = {
                "cycles": cycles,
                "sleeps": sleeps,
                "recoveries": recoveries,
                "workouts": workouts,
            }
        except requests.HTTPError as e:
            abort(
                e.response.status_code,
                description=e,
            )

        return jsonify(data)


class UserProfileResource(Resource):
    def get(self):
        whoop_client = current_app.config["WhoopClient"]
        try:
            return jsonify(whoop_client.get_profile_basic())
        except requests.HTTPError as e:
            abort(e.response.status_code, description=e)


class UserBodyMeasurementResource(Resource):
    def get(self):
        whoop_client = current_app.config["WhoopClient"]
        try:
            return jsonify(whoop_client.get_body_measurement())
        except requests.HTTPError as e:
            abort(e.response.status_code, description=e)
