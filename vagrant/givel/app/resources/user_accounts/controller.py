import boto3

from app import app
from flask import Blueprint, request
from flask_restful import Resource, Api

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound, BadRequest

from app.models import create_users_table

user_account_api_routes = Blueprint('account_api', __name__)
api = Api(user_account_api_routes)


db = boto3.client('dynamodb')

# Connect to database and create table if not already created else return Table
try:
    users = create_users_table()
    print('Users Table did not exist!')
except:
    pass


class CreateUserAccount(Resource):
    def post(self):
        """Creates User"""
        data = request.get_json(force=True)
        if not data['email'] or not data['first_name'] or not data['last_name'] or not data['password']:
            raise BadRequest('Provide all details')
        password = generate_password_hash(data['password'])
        
        try:
            user = db.put_item(
                            TableName='users', 
                            Item= {'email': {'S': data['email']},
                                 'first_name': {'S': data['first_name']},
                                 'last_name': {'S': data['last_name']},
                                 'password': {'S': password},
                                 'givel_stars': {'N': '25'},
                                 },
                            ConditionExpression='attribute_not_exists(email)',
                           )
        except:
            raise BadRequest('User already exists!')
        return user, 201

            

class UserProfile(Resource):
    def delete(self, user_email, password):
        """Deletes a User"""
        user = db.get_item(TableName='users', 
                        Key={'email': {'S': user_email}})
        try:
            if user and check_password_hash(user['Item']['password']['S'], password):
                return db.delete_item(TableName='users', 
                                Key={'email': {'S': user_email}}), 200
        except:
            raise BadRequest('User does not exist!')

    
    def get(self, user_email, password):
        """Returns User Profile"""
        user = db.get_item(TableName='users',
                       Key={'email': {'S':user_email}})
        try:
            if user and check_password_hash(user['Item']['password']['S'],
                                        password):
                return user['Item'], 200
        except:
            raise NotFound('User not found!')


    # def put(self, user_email):
    #     """Updates Users Profile"""
    #     data = request.get_json(force=True)
    #     if data['profile_picture'] or data['home'] or data['home_away']:
    #         if data ['profile_picture']:
    #             return db.update_item(TableName='users',
    #                             Key={'email': {'S': user_email}},
    #                             UpdateExpression='SET profile_picture = :picture',
    #                             ExpressionAttributeValues={
    #                                      ':picture': {'S': data['profile_picture']}}
    #                         ), 200
    #         if data['home']:
    #             # add_user = db.update_item(TableName='communities',
    #             #                     Key={'state': {'S': data['home']['state']},
    #             #                          'city': {'S': data['home']['city']}},
    #             #                     UpdateExpression='SET user_count = :count',
    #             #                     ExpressionAttributeValues={
    #             #                             ':count': {'NS': }
    #             #                         }
    #             #                     )
    #             return db.update_item(TableName='users',
    #                                 Key={'email': {'S': user_email}},
    #                                 UpdateExpression='SET home = :p',
    #                                 ExpressionAttributeValues={
    #                                          ':p': {'S': data['home']}}
    #                             ), 200
    #         if data['home_away']:
    #             return db.update_item(TableName='users',
    #                                 Key={'email': {'S': user_email}},
    #                                 UpdateExpression='SET home_away = :p',
    #                                 ExpressionAttributeValues={
    #                                          ':p': {'S': data['home_away']}}
    #                             ), 200



class UserProfilePicture(Resource):
    def get(self, user_email):
        """Returns Users Profile Picture"""
        user = db.get_item(TableName='users',
                        Key={'email': {'S': user_email}},
                        ProjectionExpression='profile_picture',
                    )
        return user['Item']['profile_picture']['S'], 200

    def put(self, user_email):
        """Updates Users Profile Picture"""
        data = request.get_json(force=True)
        if data['profile_picture']:
            return db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='SET profile_picture = :picture',
                                ExpressionAttributeValues={
                                         ':picture': {'S': data['profile_picture']}}
                            ), 200

    def delete(self, user_email):
        """Removes Users Profile Picture"""
        user = db.update_item(TableName='users',
                            Key={'email': {'S': user_email}},
                            UpdateExpression='REMOVE profile_picture')
        return 200   



api.add_resource(CreateUserAccount, '/')
api.add_resource(UserProfile, '/<user_email>/<password>',
                              '/<user_email>')
api.add_resource(UserProfilePicture, '/<user_email>/profile_picture')


