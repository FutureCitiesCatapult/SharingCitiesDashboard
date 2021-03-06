from http import HTTPStatus

from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask_restful import reqparse

from models.alert_model import AlertWidgetModel


class GetAlerts(Resource):
    """ Get alerts by user id and/or attribute id. """

    def __init__(self) -> None:
        """ Instantiate Reqparse."""
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('user_id', required=False, type=int,
                                    store_missing=False)
        self.reqparser.add_argument('attribute_id', required=False, type=str,
                                    store_missing=False)
        self.reqparser.add_argument('widget_id', required=False, type=int,
                                    store_missing=False)

    @jwt_required
    def get(self) -> (dict, HTTPStatus):
        """
        Get alerts by user id and/or attribute id.
        :return: An HTTP Response with a JSON body content containing a list of
                alerts matching the parsed POST request arguments on success,
                otherwise an empty list is returned
        """
        args = self.reqparser.parse_args()

        alerts = AlertWidgetModel.get_by_kwargs(**args)

        response_models = list()
        for alert in alerts:
            response_models.append(alert.json)

        return response_models, HTTPStatus.OK
