""" API Resource class that allows user's to activate their dashboard account """
from datetime import datetime

from flask_restful import Resource, reqparse, inputs

from db import db
from models.users import Users

class Register(Resource):
	
	parser = reqparse.RequestParser()
	parser.add_argument('email', type=str, store_missing=False, help = 'This field cannot be blank', required = True)
	parser.add_argument('password', type=str, store_missing=False,  help = 'This field cannot be blank', required = True)
	parser.add_argument('password_new', type=str, store_missing=False,  help = 'This field cannot be blank', required = True)

	def post(self) ->(str,int):
		"""
		POST requests, activate user's account and change their password
		Parameters can be passed using a POST request that contains a JSON of the following fields:
		:param fullname: users fullname
		:param email: users email address
		:param password: users password that was sent when they were added on the admin page
		:type fullname: string
		:type email: string
		:type password: string
		:return: A message that indicates whether a user has been registered. If they have not, the message indicates why not
		""" 
		args = self.parser.parse_args()
		current_user = Users.find_by_email(args['email']) #t

		if not current_user:
			return {'message': 'User {} is not authorised to access Sharing Cities Dashboard'. format(args['email'])}, 403 

		if not Users.verify_hash(args['password'].encode("utf8"), current_user.password.encode("utf8")):
			return {'message': 'The password entered does not correspond to the password sent to {}. Please try again'. format(args['email'])}, 403

		current_user.activated = True 
		current_user.password = Users.generate_hash(args["password_new"].encode("utf8")).decode("utf8")
		current_user.commit()
		return {'message': '{}\'s account has been registered. Redirect to login'. format(args['email'])}, 201

