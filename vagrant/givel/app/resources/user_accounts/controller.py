import boto3

from flask import Blueprint
from flask_restful import Resource, Api 
from app import app

from werkzeug.security import generate_password_hash, check_password_hash
from app.models import dynamodb, users

user_account_api_routes = Blueprint('account_api', __name__)

api = Api(user_account_api_routes)


class UserAccount(Resource):
   def post(self):
       data = request.get_json(force=True)
       user = dynamodb.Table('users')
       response = user.put_item(
           Item={
               'first_name': data.get('first_name'),
               'last_name': data.get('last_name'),
               'email': data.get('email'),
               'password': generate_password_hash(data.get('password'))
           })
       return 'Success'
