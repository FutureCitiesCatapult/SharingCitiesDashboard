import logging
from http import HTTPStatus

from flask import abort
from flask_jwt_extended import jwt_required, get_jwt_claims
from flask_restful import Resource
from flask_restful import reqparse

from models.pin_location_data import Tracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CreateTracker(Resource):
    """
    Create Tracker
    """

    def __init__(self) -> None:
        """
        Set required arguments for POST request
        """
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('id', required=True, type=str)
        self.reqparser.add_argument('sub_theme_id', required=True, type=int)
        self.reqparser.add_argument('description', required=False, default="",
                                    type=str)
    @jwt_required
    def post(self) -> (str, HTTPStatus):
        """
        Create new Tracker
        :param tracker_id: Tracker Id
        :param sub_theme_id: SubTheme Id
        :param description: Description of the tracker
        :return: Tracker id and an HTTPStatus code 201 (CREATED) on success,
                 otherwise a JSON error response containing The tracker id and
                 an HTTPStatus of 500 (Internal Server Error)
        """

        if not get_jwt_claims()['admin']:
            abort(HTTPStatus.FORBIDDEN.value,
                  error="administration privileges required")

        args = self.reqparser.parse_args()
        tracker = Tracker.get_by_tracker_id(args["id"])
        if tracker:
            return {"error": "Tracker already exists",
                    "tracker": tracker.json}, HTTPStatus.BAD_REQUEST

        tracker = Tracker(args["id"], args["sub_theme_id"], args["description"])

        tracker.save()
        tracker.commit()
        if Tracker.get_by_tracker_id(args["id"]):
            return tracker.json, HTTPStatus.CREATED

        return {"error": "Failed to create Tracker",
                "id": args["id"]}, HTTPStatus.INTERNAL_SERVER_ERROR
