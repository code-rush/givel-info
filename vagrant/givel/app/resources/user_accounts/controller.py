import boto3

from flask import Blueprint, request, json
from flask_restful import Resource, Api
from app import app

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound, BadRequest
from app.models import create_users_table

user_account_api_routes = Blueprint('account_api', __name__)
api = Api(user_account_api_routes)


client = boto3.client('dynamodb')

# Connect to database and create table if not already created else return Table
try:
    users = create_users_table()
    print('Users Table did not exist!')
except:
    pass


class CreateUserAccount(Resource):
    def post(self):
        data = request.get_json(force=True)
        if not data['email'] or not data['first_name'] or not data['last_name'] or not data['password']:
            raise BadRequest('Provide all details')
        password = generate_password_hash(data['password'])
        
        try:
            user = client.put_item(
                            TableName='users', 
                            Item= {'email': {'S': data['email']},
                                 'first_name': {'S': data['first_name']},
                                 'last_name': {'S': data['last_name']},
                                 'password': {'S': password},
                                 'givel_stars': {'N': '25'},
                                 },
                            ReturnValues='ALL_OLD',
                            ConditionExpression='attribute_not_exists(email)',
                           )
        except:
            raise BadRequest('User already exists!')
        # print (user['Attributes'])
        return user, 201
            

class UserProfile(Resource):
    def delete(self, user_email, password):
        user = client.get_item(TableName='users', 
                            Key={'email': {'S': user_email}})
        try:
            if user and check_password_hash(user['Item']['password']['S'],
                                            password):
                return client.delete_item(TableName='users', 
                                Key={'email': {'S': user_email}}), 200
        except:
            raise BadRequest('User does not exist!')

    
    def get(self, user_email, password):
        user = client.get_item(TableName='users',
                            Key={'email': {'S':user_email}})
        try:
            if user and check_password_hash(user['Item']['password']['S'],
                                        password):
                return user['Item'], 200
        except:
            raise NotFound('User not found!')


    def put(self, user_email):
        user = users.get_item(Key={'email': user_email})
        data = request.get_json(force=True)
        if data['picture']:
            return client.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='SET picture = :picture',
                                ExpressionAttributeValues={
                                             ':picture': {'S': data['picture']}
                                             }), 200



api.add_resource(CreateUserAccount, '/user_accounts')
api.add_resource(UserProfile, '/user_accounts/<user_email>/<password>',
                              '/user_accounts/<user_email>')


