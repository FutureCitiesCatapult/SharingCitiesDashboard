from http import HTTPStatus

from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask_restful import abort
from flask_restful import reqparse

from models.users import Users


class ChangeUserName(Resource):
    """
    API resource class which changes username and saves changes to the database
    Parameters can be passed using a POST request that contains a JSON with the following fields:
    :required: valid access JWT where the admin claim may be either true or false
    :param email: users email address
    :param fullname: users fullname
    :type email: str
    :type fullname: str
    :return: Empty string and 200 status code
    """

    def __init__(self) -> None:
        """
        Instanciates the Change users endpoint to change the users full name
        Parameters can be passed using a POST request that contains a JSON with the following fields:
        :required: valid access JWT where the admin claim may be either true or false
        :param email: users email address
        :param fullname: users fullname
        :type email: str
        :type fullname: str
        """
        self.post_reqparser = reqparse.RequestParser()
        self.post_reqparser.add_argument('email', required=True, help='email is required', location=['form', 'json'])
        self.post_reqparser.add_argument('fullname', required=True, help='fullname is required',
                                         location=['form', 'json'])

    @jwt_required
    def post(self) -> (str, int):
        """
        API resource class which changes username and saves changes to the database
        Parameters can be passed using a POST request that contains a JSON with the following fields:
        :required: valid access JWT where the admin claim may be either true or false
        :param email: users email address
        :param fullname: users fullname
        :type email: str
        :type fullname: str
        :return: Empty string and 200 status code
        """
        args = self.post_reqparser.parse_args()
        user = Users.find_by_email(args["email"])
        if not user:
            abort(HTTPStatus.NOT_FOUND.value, error='User not found.')
        user.fullname = args["fullname"]
        user.save()
        user.commit()
        return "", 200
