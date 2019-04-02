import logging
from http import HTTPStatus

from flask_restful import Resource
from flask_restful import reqparse

from models.pin_location_data import Tracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeleteTracker(Resource):
    """
    Delete Tracker
    """

    def __init__(self) -> None:
        """
        Set required arguments for POST request
        """
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('id', required=True, type=str)

    def post(self) -> (str, HTTPStatus):
        """
        Delete Tracker
        :param tracker_id: Tracker Id number
        :return: No Content with an HTTPStatus of 204 (No Content) otherwise,
                 a JSON error message with an HTTPStatus 404 (Not Found)
        """
        args = self.reqparser.parse_args()
        tracker = Tracker.get_by_tracker_id(args["id"])
        if tracker:
            tracker.delete()
            tracker.commit()
            return "", HTTPStatus.NO_CONTENT

        return {"error": "Tracker not found",
                "id": args["id"]}, HTTPStatus.NOT_FOUND
