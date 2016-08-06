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
client = boto3.client('dynamodb')

# Connect to database and create table if not already created else return Table
try:
    users = create_users_table()
    print('Users Table did not exist!')
finally:
    users = dynamodb.Table('users')
    print('Connected to users Table')
    


class CreateUserAccount(Resource):
    def post(self):
        data = request.get_json(force=True)
        if not data['email'] or not data['first_name'] or not data['last_name'] or not data['password']:
            raise BadRequest('Provide all details')
        password = generate_password_hash(data['password'])
        
        user = users.put_item(
                       Item={'email': data['email'],
                             'first_name': data['first_name'],
                             'last_name': data['last_name'],
                             'password': password,
                             'givel_stars': 25,
                             },
                             ConditionExpression='attribute_not_exists(email)'
                       )
        return user, 201
            

class UserProfile(Resource):
    def delete(self, user_email, password):
        user = users.get_item(Key={'email': user_email})
        if user == null:
            raise BadRequest('User does not exist')
        if user and check_password_hash(user['Item']['password'], password):
            return users.delete_item(Key={'email': user_email}), 200

    # def get(self, user_email, password):
    #     user = users.get_item()

    def put(self, user_email):
        # user = users.get_item(Key={'email': user_email})
        data = request.get_json(force=True)
        if data['picture']:
            return users.update_item(Key={'email':user_email},
                                     AttributeUpdates={'picture':{'Action':'PUT',
                                                                  'Value':{'S':data['picture']}
                                                                 }
                                                      }
                                    ), 200



api.add_resource(CreateUserAccount, '/user_accounts')
api.add_resource(UserProfile, '/user_accounts/<user_email>/<password>',
                              '/user_accounts/<user_email>/')


