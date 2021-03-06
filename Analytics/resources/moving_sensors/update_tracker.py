import logging
from http import HTTPStatus

from flask import abort
from flask_jwt_extended import jwt_required, get_jwt_claims
from flask_restful import Resource
from flask_restful import reqparse

from models.pin_location_data import Tracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UpdateTracker(Resource):
    """
    Update Tracker
    """

    def __init__(self) -> None:
        """
        Set required arguments for POST request
        """
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('id', required=True, type=str)
        self.reqparser.add_argument('description', required=False, default="",
                                    type=str)

    @jwt_required
    def post(self) -> (str, HTTPStatus):
        """
        Update existing Tracker
        :param tracker_id: Tracker Id number
        :param description: Description of the tracker
        :return: Tracker and an HTTPStatus code 200 (OK) otherwise a JSON error
                 message and an HTTPStatus 404 (Not Found)
        """

        if not get_jwt_claims()['admin']:
            abort(HTTPStatus.FORBIDDEN.value,
                  error="administration privileges required")

        args = self.reqparser.parse_args()
        tracker = Tracker.get_by_tracker_id(args["id"])
        if tracker:
            tracker.description = args["description"]
            tracker.save()
            tracker.commit()
            return tracker.json, HTTPStatus.OK

        return {"error": "Tracker Not Found",
                "id": args["id"]}, HTTPStatus.NOT_FOUND
