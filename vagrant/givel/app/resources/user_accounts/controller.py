import boto3

from flask import Blueprint, request, json
from flask_restful import Resource, Api
from app import app

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound, BadRequest
from app.models import create_users_table

user_account_api_routes = Blueprint('account_api', __name__)
api = Api(user_account_api_routes)


dynamodb = boto3.resource('dynamodb')

# Connect to database and create table if not already created else return Table
try:
    users = dynamodb.Table('users')
    print('Connected to users Table')
except Exception as e:
    print('Users Table does not exist!')
    users = create_users_table()


class CreateUserAccount(Resource):
    def post(self):
        data = request.get_json(force=True)
        if not data['email'] or not data['first_name'] or not data['last_name'] or not data['password']:
            raise BadRequest('Provide all details')
        password = generate_password_hash(data['password'])
        user = users.put_item(Item={'email': data['email'],
                                    'first_name': data['first_name'],
                                    'last_name': data['last_name'],
                                    'password': password,
                                    })
        return user, 201
            

class UserProfile(Resource):
    def delete(self, user_email):
        user = users.get_item(Key={'email': user_email})
        if not user:
            raise BadRequest('User does not exist')
        return users.delete_item(Key={'email': user_email}), 200



api.add_resource(CreateUserAccount, '/user_accounts')
api.add_resource(UserProfile, '/user_accounts/<user_email>')


