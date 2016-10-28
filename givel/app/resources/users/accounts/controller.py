import boto3
import datetime
import string
import random

from app.app import app, mail

from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_mail import Message

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound, BadRequest, RequestTimeout

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
    try:
        table_response = db.describe_table(TableName='users')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('Users Table exists!')
    except:
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
                                 'post_only_to_followers': {'BOOL': False},
                                 'total_stars_earned': {'N': '25'},
                                 'total_stars_shared': {'N': '0'}
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
                del response['result']['total_stars_shared']
                del response['result']['total_stars_earned']
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
            s3.delete_object(Bucket=BUCKET_NAME, Key=user_email)
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


class PostOnlyToFollowers(Resource):
    def put(self, user_email):
        response = {}
        data = request.get_json(force=True)
        value = None

        if data.get('value') != None:
            if data['value'] == 'true':
                value = True
                response['message'] = 'Post will only show up to your followers!'
            elif data['value'] == 'false':
                value = False
                response['message'] = 'Post will show up on communities and to followers!'
            else:
                raise BadRequest('The value should be either true or false.')
            user = db.update_item(TableName='users',
                        Key={'email': {'S': user_email}},
                        UpdateExpression='SET post_only_to_followers = :v',
                        ExpressionAttributeValues={
                            ':v': {'BOOL': value}
                        }
                    )
            return response, 200


class GiveStarsToFollowings(Resource):
    def put(self, user_email):
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user = db.get_item(TableName='users',
                        Key={'email': {'S': user_email}})

        if data.get('user_id') == None:
            raise BadRequest('Select a user to share stars with.')
        
        if data.get('stars') != None:
            if int(data['stars']) == 0:
                raise BadRequest('Atleast 1 star is needed to be shared')
            if int(data['stars']) > int(user['Item']['givel_stars']['N']):
                raise BadRequest('Cannot give stars more than what you have')
            else:
                add_entry_to_stars_table = db.put_item(TableName='stars_activity',
                                        Item={'email': {'S': user_email},
                                              'shared_time': {'S': date_time},
                                              'shared_to': {'S': 'user'},
                                              'shared_id': {'S': data['user_id']},
                                              'stars': {'N': data['stars']}
                                        }
                                    )
                try:
                    give_stars = db.update_item(TableName='users',
                                Key={'email': {'S': data['user_id']}},
                                UpdateExpression='SET total_stars_earned = total_stars_earned + :stars, \
                                                  givel_stars = givel_stars + :stars',
                                ExpressionAttributeValues={
                                    ':stars' : {'N': str(data['stars'])}
                                }
                            )
                except:
                    rollback_activity = db.delete_item(TableName='stars_activity',
                                        Key={'email': {'S': user_email},
                                             'shared_time': {'S': date_time}
                                        }
                                    )
                    print('caught an exception giving stars')
                    raise RequestTimeout('Try Again Later')

                try:
                    deduct_stars = db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='SET givel_stars = givel_stars - :stars, \
                                                  total_stars_shared = total_stars_shared + :stars',
                                ExpressionAttributeValues={
                                    ':stars': {'N': str(data['stars'])}
                                }
                            )
                    response['message'] = 'Stars successfully shared!'
                except:
                    rollback_activity = db.delete_item(TableName='stars_activity',
                                        Key={'email': {'S': user_email},
                                             'shared_time': {'S': date_time}
                                        }
                                    )
                    rollback_stars = db.update_item(TableName='users',
                                Key={'email': {'S': data['user_id']}},
                                UpdateExpression='SET total_stars_earned = total_stars_earned - :stars, \
                                                  givel_stars = givel_stars - :stars',
                                ExpressionAttributeValues={
                                    ':stars' : {'N': str(data['stars'])}
                                }
                            )
                    print('caught an exception deducting stars!')
                    raise RequestTimeout('Try again later!')

                return response, 200


class ForgotPassword(Resource):
    def post(self):
        """Resets password and sends notification email"""
        response = {}
        data = request.get_json(force=True)

        if data.get('email') == None:
            raise BadRequest('Type in your email address')
        else:
            chars = string.ascii_lowercase + string.digits
            pwd_size = 8
            random_pwd = ''.join((random.choice(chars)) for x in range(pwd_size))

            update_pwd = db.update_item(TableName='users',
                            Key={'email': {'S': data['email']}},
                            UpdateExpression='SET password = :pwd',
                            ExpressionAttributeValues={
                                ':pwd': {'S': generate_password_hash(random_pwd)}
                            }
                        )

            try:
                send_mail = Message('Forgot Password',
                                    sender='parikh.japan30@gmail.com',
                                    recipients=['{}'.format(data['email'])]
                                )
                send_mail.body = 'New Password = {}'.format(random_pwd)
                mail.send(send_mail)
                print (random_pwd)
                response['message'] = 'Request sent successfully.'
            except:
                response['message'] = 'Request Failed!'

            return response, 200




api.add_resource(UserAccount, '/')
api.add_resource(UserProfilePicture, '/<user_email>/picture')
api.add_resource(UserCommunities, '/<user_email>/communities/<community>')
api.add_resource(UserLogin, '/login')
api.add_resource(ChangePassword, '/<user_email>/password')
api.add_resource(PostOnlyToFollowers, '/settings/post_only_to_followers/<user_email>')
api.add_resource(GiveStarsToFollowings, '/stars/share/<user_email>')
api.add_resource(ForgotPassword, '/settings/forgot_password')

