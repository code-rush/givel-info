import boto3

from app import app
from flask import Blueprint, request
from flask_restful import Resource, Api

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound, BadRequest

from app.models import create_users_table
from app.helper import upload_file, check_if_community_exists
from app.helper import update_member_counts

user_account_api_routes = Blueprint('account_api', __name__)
api = Api(user_account_api_routes)


BUCKET_NAME = 'gprofilepictures'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


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


class UserAccount(Resource):
    def post(self):
        """Creates User"""
        data = request.get_json(force=True)
        if not data['email'] or not data['first_name'] or not data['last_name'] or not data['password']:
            raise BadRequest('Provide all details')
        password = generate_password_hash(data['password'])
        response = {}
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
            response['message'] = 'User successfully created!'
            return response, 201
        except:
            raise BadRequest('User already exists!')
            

    def delete(self):
        """Deletes a User"""
        user_data = request.get_json(force=True)
        user = db.get_item(TableName='users', 
                        Key={'email': {'S': user_data['email']}})
        response = {}
        try:
            if user and check_password_hash(user['Item']['password']['S'], user_data['password']):
                delete_user = db.delete_item(TableName='users', 
                                Key={'email': {'S': user_data['email']}})
                response['message'] = 'User deleted!'
                return response, 200
            else:
                response['message'] = 'Incorrect Password!'
                return response ,401
        except:
            raise BadRequest('User does not exist!')


class UserLogin(Resource):
    def post(self):
        """Returns User Profile"""
        user_data = request.get_json(force=True)
        user = db.get_item(TableName='users',
                       Key={'email': {'S':user_data['email']}})
        response = {}
        try:
            if user and check_password_hash(user['Item']['password']['S'],
                                        user_data['password']):
                response['message'] = 'User successfully Logged In!'
                response['result'] = user['Item']
                return response, 200
            else:
                response['message'] = 'Incorrect Password!'
                return response, 401
        except:
            raise NotFound('User not found!')



class UserProfilePicture(Resource):
    def get(self, user_email):
        """Returns Users Profile Picture"""
        response = {}
        try:
            user = db.get_item(TableName='users',
                            Key={'email': {'S': user_email}},
                            ProjectionExpression='profile_picture',
                        )
            response['message'] = 'Success!'
            response['result'] = user['Item']
            return response, 200
        except:
            raise NotFound('Picture not found!')

    def post(self, user_email):
        """Updates Users Profile Picture"""
        picture = request.files['picture']
        response = {}
        try:
            picture_file = upload_file(picture, BUCKET_NAME, user_email, ALLOWED_EXTENSIONS)
            if picture_file != None:
                user = db.update_item(TableName='users',
                                    Key={'email': {'S': user_email}},
                                    UpdateExpression='SET profile_picture = :picture',
                                    ExpressionAttributeValues={
                                             ':picture': {'S': picture_file}}
                                )
                response['message'] = 'File uploaded!'
            else:
                response ['message'] = 'File not allowed!'
            return response, 200
        except:
            raise BadRequest('Invalid Operation!')

    def delete(self, user_email):
        """Removes Users Profile Picture"""
        response = {}
        user = db.get_item(TableName='users',
                            Key={'email': {'S': user_email}}
                        )

        if user['Item'].get('profile_picture') != None:
            user = db.update_item(TableName='users',
                               Key={'email': {'S': user_email}},
                               UpdateExpression='REMOVE profile_picture')
            delete_image = s3.delete_object(Bucket=BUCKET_NAME, Key=user_email)
            response['message'] = 'File deleted!'
            return response, 200
        else:
            raise BadRequest('Picture not found!')


class UserCommunities(Resource):
    def put(self, user_email, community):
        """Updates User Communities"""
        data = request.get_json(force=True)
        response = {}
        user = db.get_item(TableName='users',
                            Key={'email': {'S': user_email}}
                        )

        if community == 'home':
            city, state, exists = check_if_community_exists(data['community'])
            if exists == True:
                try:
                    user_home = db.update_item(TableName='users',
                                    Key={'email': {'S': user_email}},
                                    UpdateExpression='SET home = :p',
                                    ExpressionAttributeValues={
                                             ':p': {'S': data['community']}}
                                )
                    update_member_counts(city, state, 'add')
                    response['message'] = 'home community successfully added!'
                    return response, 200
                except:
                    raise BadRequest('Failed to add community!')
            else:
                raise BadRequest('{} community does not exist!'.format(data['community']))


        if community == 'home_away':
            if user['Item'].get('home') == None:
                raise BadRequest('To add a home_away community, you ' + \
                            'need to add a home community first')
            else:
                city, state, exists = check_if_community_exists(data['community'])
                if exists == True:
                    try:
                        user_home_away = db.update_item(TableName='users',
                                            Key={'email': {'S': user_email}},
                                            UpdateExpression='SET home_away = :p',
                                            ExpressionAttributeValues={
                                                     ':p': {'S': data['community']}}
                                        )
                        update_member_counts(city, state, 'add')
                        response['message'] = 'home_away community successfully added!'
                        return response, 200
                    except:
                        raise BadRequest('Failed to add community!')
                else:
                    raise BadRequest('{} community does not exist!'.format(data['community']))

    def delete(self, user_email, community):
        """Unfollow Community"""
        user = db.get_item(TableName='users',
                        Key={'email': {'S': user_email}}
                    )
        response = {}

        if user['Item'].get(community) == None:
            raise BadRequest('Community not found!')
        elif community == 'home':
            comm = user['Item']['home']['S'].rsplit(' ', 1)
            state = comm[1]
            city = comm[0][:-1]
            try:
                if user['Item'].get('home_away') != None:
                    home = db.update_item(TableName='users',
                                    Key={'email': {'S': user_email}},
                                    UpdateExpression='SET home = :home',
                                    ExpressionAttributeValues={
                                        ':home': {'S': user['Item']['home_away']['S']}
                                    }
                                )
                    delete_home_away = db.update_item(TableName='users',
                                    Key={'email': {'S': user_email}},
                                    UpdateExpression='REMOVE home_away'
                                )
                else:
                    delete_home = db.update_item(TableName='users',
                                        Key={'email': {'S': user_email}},
                                        UpdateExpression='REMOVE home'
                                    )
                update_member_counts(city, state, 'remove')
                response['message'] = 'Successfully deleted home community!'
            except:
                raise BadRequest('Failed to add community!')
        elif community == 'home_away':
            comm = user['Item']['home_away']['S'].rsplit(' ', 1)
            state = comm[1]
            city = comm[0][:-1]
            try:
                delete_home_away = db.update_item(TableName='users',
                                    Key={'email': {'S': user_email}},
                                    UpdateExpression='REMOVE home_away'
                                )
                update_member_counts(city, state, 'remove')
                response['message'] = 'Successfully deleted home community!'
            except:
                raise BadRequest('Failed to add community!')
        return response, 200


class ChangePassword(Resource):
    """Change user's password"""
    def put(self, user_email):
        response = {}
        user = db.get_item(TableName='users', 
                            Key={'email': {'S': user_email}
                            }
                        )
        user_data = request.get_json(force=True)
        if user_data.get('current_password') == None \
          or user_data.get('new_password') == None:
            raise BadRequest('Please provide all details')
        else:
            if check_password_hash(user['Item']['password']['S'], \
                                    user_data['current_password']):
                update_pwd = db.update_item(TableName='users',
                                        Key={'email': {'S': user_email}},
                                        UpdateExpression='SET password = :pwd',
                                        ExpressionAttributeValues={
                                            ':pwd': {'S': generate_password_hash(user_data['new_password'])}
                                        },
                                        ReturnValues='UPDATED_NEW'
                                    )
                response['message'] = 'Password Updated!'
            else:
                response['message'] = 'Please enter correct current password'

            return response, 200


api.add_resource(UserAccount, '/')
api.add_resource(UserProfilePicture, '/<user_email>/picture')
api.add_resource(UserCommunities, '/<user_email>/communities/<community>')
api.add_resource(UserLogin, '/login')
api.add_resource(ChangePassword, '/<user_email>/password')

