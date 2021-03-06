from http import HTTPStatus

from flask import abort
from flask import jsonify
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse

from models.users import Users


class UsersList(Resource):
    """
    API resource class that returns a list of users from the database

    Parameters can be passed using a POST request that contains the following fields in the url:
    :param  limit: the max count of users to be returned
    :type limit: int
    :returns: A list of widgets with a maximum length of limit and a status code 200
    """
    user_fields = {"id": fields.Integer,
                   "email": fields.String,
                   "fullname": fields.String,
                   "password": fields.String,
                   "activated": fields.Boolean,
                   "admin": fields.Boolean
                   }

    def __init__(self):
        """
        Instantiates the list user endpoint
        Parameters can be passed using a GET request that contains the following fields in the url:
        :param  limit: the max count of users to be returned
        :type limit: int
        """
        self.get_reqparser = reqparse.RequestParser()
        self.get_reqparser.add_argument("limit", required=True, help='limit is required', location=['form', 'json'])

    # Returns a list of users
    @jwt_required
    def post(self) -> (str, int):
        """
        Get a list of user with from the database
        :param  limit: the max count of widgets to be returned
        :type limit: int
        :returns: A list of widgets with a maximum length of limit and a status code 200
        """
        args = self.get_reqparser.parse_args()

        if not get_jwt_claims()['admin']:
           return {"message": "not authorized"}, 403

        users = (marshal(user, self.user_fields)
                 for user in Users.query.filter_by().limit(args["limit"]))
        # Format user data

        user_list = []
        for user in users:
            user_list.append(user)

        return {"users": user_list}, 200
