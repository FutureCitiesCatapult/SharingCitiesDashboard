from http import HTTPStatus

import bcrypt
from flask import jsonify
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask_restful import abort
from flask_restful import reqparse
from sqlalchemy import exc

from models.users import Users


class ChangeUserPassword(Resource):

    def __init__(self):

        # Create User (Post request parser)
        self.post_reqparser = reqparse.RequestParser()
        self.post_reqparser.add_argument('email', help='email is required', location=['form', 'json'])
        self.post_reqparser.add_argument('password', required=True, location=['form', 'json'])
        self.post_reqparser.add_argument('verify_password', required=True, location=['form', 'json'])
        super().__init__()

    @jwt_required
    def post(self):
        args = self.post_reqparser.parse_args()
        user = None

        #User must be an admin
        if not get_jwt_claims()['admin']:
            abort(HTTPStatus.FORBIDDEN.value, error="administration privileges required")

        #get user instance using email
        if args["email"]:
            user = Users.find_by_email(args["email"])
            if not user:
                abort(HTTPStatus.BAD_REQUEST.value, error="User not found")

        if args["password"] == args["verify_password"]:
            user.password = Users.generate_hash(args["password"].encode("utf-8"))

        try:
            user.save()
            user.commit()
        except exc.SQLAlchemyError:
            abort(HTTPStatus.BAD_REQUEST.value, error="User password not changed")

        return {"user": "{} password changed".format(args["email"])}, 201


