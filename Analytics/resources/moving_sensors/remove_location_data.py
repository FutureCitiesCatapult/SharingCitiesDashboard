from datetime import datetime
from http import HTTPStatus

from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask_restful import reqparse

from models.pin_location_data import LocationData


class WindowLocationData(Resource):
    """
    Delete All Data outside of the specified Date period
    """

    def __init__(self) -> None:
        """
        Set required arguments for POST request
        """
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('tracker_id', required=False,
                                    store_missing=False, type=str)
        self.reqparser.add_argument('days', required=False, default=365,
                                    type=int)
        self.reqparser.add_argument('start_date', required=False,
                                    store_missing=False,
                                    type=lambda x: datetime.strptime(x,
                                                                     '%d/%m/%Y'))

    @jwt_required
    def post(self) -> (str, HTTPStatus):
        """
        Delete All Data outside of the specified period
        :param tracker_id: Tracker Id
        :param days: Number of days before start date to keep
        :param start_date: Date of newest data to keep (format: %d/%m/%Y)
        :return: No Content in body and an HTTPStatus 204 (No Content) on
                 success
        """
        args = self.reqparser.parse_args()
        results = LocationData.windows_data(**args)
        return results, HTTPStatus.OK
