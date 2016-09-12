import boto3

from app import app
from flask import Blueprint, request
from flask_restful import Resource, Api

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound, BadRequest

from app.models import create_users_table
from app.helper import upload_file

user_account_api_routes = Blueprint('account_api', __name__)
api = Api(user_account_api_routes)


BUCKET_NAME = 'profilepictures'


db = boto3.client('dynamodb')
s3 = boto3.client('s3')

# Connect to database and create table if not already created else return Table
try:
    table_response = db.describe_table(TableName='users')
    if table_response['Table']['TableStatus'] == 'ACTIVE':
        print('Users Table exists!')
    else:
        users = create_users_table()
        print('Users Table created!')
except:
    pass

# Create bucket
try:
    create_bucket = client.create_bucket(
                        Bucket=BUCKET_NAME,
                        CreateBucketConfiguration={
                            'LocationConstraint': 'us-west-2'
                        }
                    )

    print (create_bucket['Location'])
except:
    pass


class UserAccount(Resource):
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
        return 201
            

    def delete(self):
        """Deletes a User"""
        user_data = request.get_json(force=True)
        user = db.get_item(TableName='users', 
                        Key={'email': {'S': user_data['email']}})
        incorrect_password_message = {}
        try:
            if user and check_password_hash(user['Item']['password']['S'], user_data['password']):
                delete_user = db.delete_item(TableName='users', 
                                Key={'email': {'S': user_data['email']}})
                return 200
            else:
                incorrect_password_message['message'] = 'Password Incorrect!'
                return incorrect_password_message ,401
        except:
            raise BadRequest('User does not exist!')


class UserLogin(Resource):
    def post(self):
        """Returns User Profile"""
        user_data = request.get_json(force=True)
        user = db.get_item(TableName='users',
                       Key={'email': {'S':user_data['email']}})
        incorrect_password_message = {}
        try:
            if user and check_password_hash(user['Item']['password']['S'],
                                        user_data['password']):
                return user['Item'], 200
            else:
                incorrect_password_message['message'] = 'Password Incorrect!'
                return incorrect_password_message, 401
        except:
            raise NotFound('User not found!')



class UserProfilePicture(Resource):
    def get(self, user_email):
        """Returns Users Profile Picture"""
        user = db.get_item(TableName='users',
                        Key={'email': {'S': user_email}},
                        ProjectionExpression='profile_picture',
                    )
        picture_file = s3.download_file(BUCKET_NAME, user_email, user['Item']['profile_picture']['S'])
        return picture_file, 200

    def put(self, user_email):
        """Updates Users Profile Picture"""
        picture = request.files['file']
        picture_file = upload_file(picture, BUCKET_NAME, user_email)
        return db.update_item(TableName='users',
                            Key={'email': {'S': user_email}},
                            UpdateExpression='SET profile_picture = :picture',
                            ExpressionAttributeValues={
                                     ':picture': {'S': picture_file}}
                        ), 200

    def delete(self, user_email):
        """Removes Users Profile Picture"""
        user = db.update_item(TableName='users',
                            Key={'email': {'S': user_email}},
                            UpdateExpression='REMOVE profile_picture')
        return user['Item'], 200   


class UserCommunities(Resource):
    def put(self, user_email, community):
        """Updates User Communities"""
        data = request.get_json(force=True)

        if community == 'home':
            user = db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='SET home = :p',
                                ExpressionAttributeValues={
                                         ':p': {'S': data[community]}}
                            )
            return 200

        if community == 'home_away':
            user = db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='SET home_away = :p',
                                ExpressionAttributeValues={
                                         ':p': {'S': data[community]}}
                            )
            return 200  

    def delete(self, user_email, community):
        """Unfollow Community"""
        user = db.get_item(TableName='users',
                        Key={'email': {'S': user_email}})

        if community == 'home':
            if user['home_away']:
                home = db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='SET home = :home',
                                ExpressionAttributeValues={
                                    ':home': {'S': user['home_away'['S']]}
                                }
                            )
                delete_home_away = db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='REMOVE home_away'
                            )
                return 200
            else:
                return  db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='REMOVE home'
                            ), 200


        if community == 'home_away':
            return db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='REMOVE home_away'
                            ), 200



api.add_resource(UserAccount, '/')
api.add_resource(UserProfilePicture, '/<user_email>/picture')
api.add_resource(UserCommunities, '/<user_email>/communities/<community>')
api.add_resource(UserLogin, '/login')


