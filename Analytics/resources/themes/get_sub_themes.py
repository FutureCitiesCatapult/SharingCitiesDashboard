from http import HTTPStatus

from flask_jwt_extended import jwt_required, get_jwt_claims
from flask_restful import Resource
from flask_restful import reqparse

from models.theme import SubTheme


class GetSubThemes(Resource):
    """
    Endpoint used to fetch units from the database table 'unit'
    Parameters can be passed using a POST request that contains a JSON with the following fields:
    :param limit: the maximum number of entries to return
    :param _type: the unit type
    :param id: the unit identification number
    :type limit: int
    :type _type: str
    :type id: str
    """

    def __init__(self) -> None:
        """
        Instantiates the endpoint to get a unit from the database table unit.
        """
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('limit', required=False, store_missing=False, type=int)
        self.reqparser.add_argument('name', required=False, store_missing=False, type=str)
        self.reqparser.add_argument('id', required=False, store_missing=False, type=str)
        self.reqparser.add_argument('theme_id', required=False, store_missing=False, type=str)

    @jwt_required
    def get(self) -> ([SubTheme], HTTPStatus):
        """
        Fetches all theme entries
        Parameters can be passed using a POST request that contains a JSON with the following fields:
        :param limit: the maximum number of entries to return
        :param _type: the unit type
        :param id: the unit identification number
        :type limit: int
        :type _type: str
        :type id: str

        :return: a list of Unit/s and an HTTPStatus code of 200 on succcess otherwise a list with a single item
         and a http status code 404 is returned
        """
        # is the user an admin user?
        if not get_jwt_claims()['admin']:
            return {"message": "Not Authorized."}, HTTPStatus.UNAUTHORIZED

        # Get arguments passed in POST request
        args = self.reqparser.parse_args()

        # pdb.set_trace()
        # fetch themes using arguments passed in post request
        subthemes = []
        if "id" in args:
            subtheme = SubTheme.get_by(id=args["id"])
            if subtheme:
                subthemes.append(subtheme.json())

        elif "name" in args:
            subtheme = SubTheme.get_by_name(args["name"])
            if subtheme:
                subthemes.append(subtheme.json())

        elif "theme_id" in args:
            [subthemes.append(subtheme.json()) for subtheme in SubTheme.get_by_theme_id(args["theme_id"])]

        else:
            [subthemes.append(subtheme.json()) for subtheme in SubTheme.get_all()]

        # were any themes found in the database?
        if len(subthemes) < 1:
            # no themes were found
            return {"error": "No themes found"}, HTTPStatus.NOT_FOUND

        if "limit" in args:
            try:
                subthemes = subthemes[:int(args["limit"])]
            except ValueError:
                return {"error": "Limit parsed is not an int"}

        # themes were found
        return subthemes, HTTPStatus.OK
