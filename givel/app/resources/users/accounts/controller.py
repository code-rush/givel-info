import boto3
import datetime
import string, random

from app.app import app, mail
# from app.plugin import login_manager

from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_mail import Message

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound, BadRequest, RequestTimeout

from app.models import create_users_table, create_notifications_table

from app.helper import (upload_file, check_if_community_exists,
                        update_member_counts, check_if_user_exists,
                        check_if_user_following_user, get_user_details,
                        check_if_user_liked, check_if_user_starred,
                        check_if_user_starred, check_if_taking_off,
                        check_if_user_commented, check_if_challenge_accepted,
                        update_notifications_activity_page,
                        get_challenge_accepted_users,
                        check_if_post_added_to_favorites)


user_account_api_routes = Blueprint('account_api', __name__)
api = Api(user_account_api_routes)

user_profile_api_routes = Blueprint('profile_api', __name__)
profile_api = Api(user_profile_api_routes)


BUCKET_NAME = 'gprofilepictures'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


db = boto3.client('dynamodb')
s3 = boto3.client('s3')


STATES = {
    'Arizona': 'AZ',
    'California': 'CA',
    'Colorado': 'CO',
    'DC': 'D.C.',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Missouri': 'MO',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Virginia': 'VA',
    'Washington': 'WA',
    'Wisconsin': 'WI',
}

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


def follow_greg(user_id):
    add_following = db.put_item(TableName='following_activity',
                                Item={'id1': {'S': user_id},
                                      'id2': {'S': 'greg@givel.co'},
                                      'type': {'S': 'user'},
                                      'following': {'S': 'True'},
                                      'follower': {'S': 'False'}
                                }
                            )
    add_follower = db.put_item(TableName='following_activity',
                                Item={'id1': {'S': 'greg@givel.co'},
                                      'id2': {'S': user_id},
                                      'type': {'S': 'user'},
                                      'following': {'S': 'False'},
                                      'follower': {'S': 'True'}
                                }
                            )


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
                                 'total_stars_earned': {'N': '25'},
                                 'total_stars_shared': {'N': '0'}
                                 },
                            ConditionExpression='attribute_not_exists(email)',
                           )
            follow = follow_greg(data['email'])
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
                # updates member counts in communities
                if user['Item']['home'] != None:
                    comm = user['Item']['home']['S'].rsplit(' ', 1)
                    state = comm[1]
                    city = comm[0][:-1]
                    update_member_counts(city, state, 'remove')
                if user['Item']['home_away'] != None:
                    comm = user['Item']['home']['S'].rsplit(' ', 1)
                    state = comm[1]
                    city = comm[0][:-1]
                    update_member_counts(city, state, 'remove')

                # deletes the user
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

        user_authenticated = False
        try:
            if user and check_password_hash(user['Item']['password']['S'],
                                        user_data['password']):
                user_authenticated = True
                response['message'] = 'User successfully Logged In!'
                response['result'] = user['Item']
                del response['result']['password']
                del response['result']['total_stars_shared']
                del response['result']['total_stars_earned']
                del response['result']['givel_stars']
            else:
                response['message'] = 'Incorrect Password!'

            response['user_authenticated'] = user_authenticated
            
            return response, 200
        except:
            raise NotFound('User not found!')



class UserProfilePicture(Resource):
    def get(self, user_email):
        """Returns Users Profile Picture"""
        response = {}
        try:
            user_exists = check_if_user_exists(user_email)
            if user_exists == True:
                user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                ProjectionExpression='profile_picture',
                            )
                response['message'] = 'Success!'
                response['result'] = user['Item']
                return response, 200
            else:
                response['message'] = 'User not found!'
                return response, 404
        except:
            raise NotFound('Picture not found!')

    def post(self, user_email):
        """Updates Users Profile Picture"""
        picture = request.files['picture']
        response = {}
        try:
            user_exists = check_if_user_exists(user_email)
            if user_exists == True:
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
            else:
                response['message'] = 'User not found!'
                return response, 404              
        except:
            raise BadRequest('Request failed.')

    def delete(self, user_email):
        """Removes Users Profile Picture"""
        response = {}
        user_exists = check_if_user_exists(user_email)
        if user_exists == True:
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
        else:
            response['message'] = 'User not found!'
            return response, 404


class GetUsersStars(Resource):
    def get(self, user_email):
        response = {}

        user = db.get_item(TableName='users', 
                            Key={'email': {'S': user_email}})

        if user.get('Item') == None:
            raise BadRequest('User does not exist. Please register the user.')
        else:
            response['message'] = 'Request successful.'
            response['result'] = {}
            response['result']['stars'] = user['Item']['givel_stars']
            return response, 200


class UserCommunities(Resource):
    def put(self, user_email, community):
        """Updates User Communities"""
        data = request.get_json(force=True)
        response = {}

        user_exists = check_if_user_exists(user_email)
        if user_exists == True:
            user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}}
                            )

            if community == 'home':
                city, state, exists = check_if_community_exists(data['community'])
                if exists == True:
                    state_abbr = STATES[state]
                    comm = city + ', ' + state_abbr
                    try:
                        user_home = db.update_item(TableName='users',
                                        Key={'email': {'S': user_email}},
                                        UpdateExpression='SET home = :p',
                                        ExpressionAttributeValues={
                                                 ':p': {'S': comm}}
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
                        state_abbr = STATES[state]
                        comm = city + ', ' + state_abbr
                        try:
                            user_home_away = db.update_item(TableName='users',
                                                Key={'email': {'S': user_email}},
                                                UpdateExpression='SET home_away = :p',
                                                ExpressionAttributeValues={
                                                         ':p': {'S': comm}}
                                            )
                            update_member_counts(city, state, 'add')
                            response['message'] = 'home_away community successfully added!'
                            return response, 200
                        except:
                            raise BadRequest('Failed to add community!')
                    else:
                        raise BadRequest('{} community does not exist!'.format(data['community']))
        else:
            raise BadRequest('Request Failed! User not found. Check if ' \
                             + 'user_email is correct and try again later.')

    def delete(self, user_email, community):
        """Unfollow Community"""
        response = {}

        user_exists = check_if_user_exists(user_email)
        if user_exists == True:
            user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}}
                            )
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
        else:
            raise BadRequest('Request Failed! User not found. Check if ' \
                             + 'user_email is correct and try again later.')


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
            raise BadRequest('Please provide both old and new password.')
        else:
            if check_password_hash(user['Item']['password']['S'], \
                                    user_data['current_password']):
                update_pwd = db.update_item(TableName='users',
                                        Key={'email': {'S': user_email}},
                                        UpdateExpression='SET password = :pwd',
                                        ExpressionAttributeValues={
                                            ':pwd': {
                                                'S': generate_password_hash(
                                                  user_data['new_password'])}
                                        }
                                    )
                response['message'] = 'Password Updated!'
            else:
                response['message'] = 'Please enter correct current password'

            return response, 200


class GiveStarsToFollowings(Resource):
    def put(self, user_email):
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

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
                                              'stars': {'N': str(data['stars'])}
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
                    notification = db.put_item(TableName='notifications',
                                            Item={'notify_to': {'S': data['user_id']},
                                                  'creation_time': {'S': date_time},
                                                  'email': {'S': user_email},
                                                  'notify_for': {'S': 'stars'},
                                                  'from': {'S': 'follower'},
                                                  'checked': {'BOOL': False},
                                                  'stars': {'N': str(data['stars'])}
                                            }
                                        )
                    update_notifications_activity_page(data['user_id'], False)
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
                    rollback_notification = db.delete_item(TableName='notifications',
                                            Key={'notify_to': {'S': data['user_id']},
                                                 'creation_time': {'S': date_time}
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


class GetUsersStarsDetails(Resource):
    def get(self, user_email):
        """Gets user's stars account details."""
        response = {}
        user_exists = check_if_user_exists(user_email)

        if not user_exists:
            raise BadRequest('User does not exist.')

        user = db.get_item(TableName='users', 
                          Key={'email': {'S': user_email}})

        result = {}
        result['sign_up_bonus'] = {}
        result['others_kind_acts'] = user['Item']['total_stars_earned']
        result['sign_up_bonus']['N'] = '25'
        result['my_kind_acts'] = user['Item']['total_stars_shared']
        result['stars_balance'] = user['Item']['givel_stars']

        response['message'] = 'Request successful.'
        response['result'] = result

        return response, 200


class GetUsersProfile(Resource):
    def post(self, user_email):
        """Returns user's profile"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user_id.')

        user_profile = db.get_item(TableName='users',
                        Key={'email': {'S':data['user_id']}})

        user_following = check_if_user_following_user(user_email, 
                                                  data['user_id'])
        name, picture, home = get_user_details(data['user_id'])

        profile_details = {}

        if user_profile['Item'] != None:
            profile_details['user'] = {}
            profile_details['user']['name'] = {}
            profile_details['user']['name']['S'] = name
            profile_details['user']['profile_picture'] = {}
            profile_details['user']['profile_picture']['S'] = picture
            profile_details['user']['home_community'] = {}
            profile_details['user']['home_community']['S'] = home
            profile_details['user']['following'] = {}
            profile_details['user']['following']['BOOL'] = user_following

            response['message'] = 'Request successful!'
            response['result'] = profile_details
        else:
            response['message'] = 'User not found!'

        return response, 200


class GetUsersProfileFollowers(Resource):
    def post(self, user_email):
        """Returns user's followers"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id.')

        followers = []
        try:
            if data.get('last_evaluated_key') != None:
                users = db.query(TableName='following_activity',
                                Limit=200,
                                IndexName='id2-following',
                                KeyConditionExpression='id2 = :id and \
                                                        following = :f',
                                ExpressionAttributeValues={
                                    ':id': {'S': data['user_id']},
                                    ':f': {'S': 'True'}
                                },
                                ExclusiveStartKey=data['last_evaluated_key'],
                                ScanIndexForward=False
                            )
            else:
                users = db.query(TableName='following_activity',
                                Limit=200,
                                IndexName='id2-following',
                                KeyConditionExpression='id2 = :id and \
                                                        following = :f',
                                ExpressionAttributeValues={
                                    ':id': {'S': data['user_id']},
                                    ':f': {'S': 'True'}
                                },
                                ScanIndexForward=False
                            )

            if users.get('Items') != []:
                for follower in users['Items']: 
                    follower_exists = check_if_user_exists(
                                        follower['id1']['S'])
                    if follower_exists:
                        user_name, photo, home = get_user_details(
                                                    follower['id1']['S'])
                        following_follower = check_if_user_following_user(
                                        user_email, follower['id1']['S'])

                        f = {}
                        f['user'] = {}
                        f['user']['name'] = {}
                        f['user']['id'] = {}
                        f['user']['home_community'] = {}
                        f['user']['name']['S'] = user_name
                        f['user']['id']['S'] = follower['id1']['S']
                        f['user']['home_community']['S'] = home
                        if photo != None:
                            f['user']['profile_picture'] = {}
                            f['user']['profile_picture']['S'] = photo
                        f['user']['following'] = {}
                        f['user']['following']['BOOL'] = following_follower

                        followers.append(f)

            if users.get('LastEvaluatedKey') != None:
                response['last_evaluated_key'] = users['LastEvaluatedKey']

            response['message'] = 'Request successful.'
            response['result'] = followers
        except:
            response['message'] = 'Request failed. Please try again later.'

        return response, 200


class GetUsersProfileFollowings(Resource):
    def post(self, user_email):
        """Returns user's followings"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id in user_id.')

        followings = []
        try:
            if data.get('last_evaluated_key') != None:
                users = db.query(TableName='following_activity',
                                IndexName='id1-following',
                                Limit=200,
                                KeyConditionExpression='id1 = :id and \
                                                      following = :f',
                                ExpressionAttributeValues={
                                    ':id': {'S': data['user_id']},
                                    ':f': {'S': 'True'}
                                },
                                ExclusiveStartKey=data['last_evaluated_key'],
                                ScanIndexForward=False
                            )
            else:
                users = db.query(TableName='following_activity',
                                IndexName='id1-following',
                                Limit=200,
                                KeyConditionExpression='id1 = :id and \
                                                      following = :f',
                                ExpressionAttributeValues={
                                    ':id': {'S': data['user_id']},
                                    ':f': {'S': 'True'}
                                },
                                ScanIndexForward=False
                            )

            if users.get('Items') != []:
                for following in users['Items']:
                    f = {}
                    f['followings'] = {}
                    f['followings']['id'] = {}
                    f['followings']['name'] = {}
                    if following['type']['S'] == 'user':
                        following_user_exists = check_if_user_exists(
                                                following['id2']['S'])
                        if following_user_exists:
                            user_name, photo, home = get_user_details(
                                                   following['id2']['S'])
                            following_user = check_if_user_following_user(
                                        user_email, following['id2']['S'])
                            f['followings']['home_community'] = {}
                            f['followings']['id'] = following['id2']
                            f['followings']['name']['S'] = user_name
                            f['followings']['home_community']['S'] = home
                            f['followings']['type'] = {}
                            f['followings']['type']['S'] = 'user'
                            f['followings']['following'] = {}
                            f['followings']['following']['BOOL'] = following_user
                            if photo != None:
                                f['followings']['profile_picture'] = {}
                                f['followings']['profile_picture']['S'] = photo
                            followings.append(f)
                    else:
                        org = db.get_item(TableName='organizations',
                            Key={'name': {'S': following['id2']['S']}})
                        following_org = check_if_user_following_user(
                                        user_email, following['id2']['S'])

                        if org.get('Item') != None:
                            f['followings']['type'] = {}
                            f['followings']['type']['S'] = 'organization'
                            f['followings']['id']['S'] = following['id2']['S']
                            f['followings']['name']['S'] = org['Item']\
                                                              ['name']['S']
                            f['followings']['profile_picture'] = org['Item']\
                                                                  ['picture']
                            f['followings']['following'] = {}
                            f['followings']['following']['BOOL'] = following_org
                            followings.append(f)

            if users.get('LastEvaluatedKey') != None:
                response['last_evaluated_key'] = users['LastEvaluatedKey']

            response['message'] = 'Request successful.'
            response['result'] = followings
        except:
            response['message'] = 'Request failed. Try again later.'

        return response, 200


class GetUsersProfileChallenges(Resource):
    def post(self, user_email):
        """Returns user's challenges"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id in user_id.')

        if data.get('last_evaluated_key') == None:
            user_challenges = db.query(TableName='challenges_activity',
                                Limit=50,
                                Select='ALL_ATTRIBUTES',
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': data['user_id']},
                                },
                                ScanIndexForward=False,
                            )
        else:
            user_challenges = db.query(TableName='challenges_activity',
                                Limit=50,
                                Select='ALL_ATTRIBUTES',
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': data['user_id']},
                                },
                                ScanIndexForward=False,
                            )

        if user_challenges.get('LastEvaluatedKey') != None:
            response['last_evaluated_key'] = user_challenges['LastEvaluatedKey']

        feeds = []

        try:
            for challenges in user_challenges['Items']:
                c_id = challenges['challenge_id']['S'].rsplit('_', 1)[0]
                c_key = challenges['challenge_id']['S'].rsplit('_', 1)[1]

                challenge = db.get_item(TableName='challenges',
                                        Key={'email': {'S': c_id},
                                             'creation_time': {'S': c_key}
                                        }
                                    )

                user_name, profile_picture, home = get_user_details(
                                                challenge['Item']['email']['S'])
                if user_name == None:
                    pass
                else:
                    feed_id = challenges['challenge_id']['S']
                    liked = check_if_user_liked(feed_id, user_email)
                    starred = check_if_user_starred(feed_id, user_email)
                    commented = check_if_user_commented(feed_id, user_email)
                    taking_off = check_if_taking_off(feed_id, 'challenges')
                    accepted, state, ac_time = check_if_challenge_accepted(
                                                  feed_id, user_email)
                    accepted_users_list = get_challenge_accepted_users(
                                                    feed_id, user_email)

                    challenge['Item']['user'] = {}
                    challenge['Item']['user']['name'] = {}
                    challenge['Item']['user']['profile_picture'] = {}
                    challenge['Item']['user']['id'] = challenge['Item']['email']
                    challenge['Item']['user']['name']['S'] = user_name
                    challenge['Item']['user']['profile_picture']['S'] = profile_picture
                    challenge['Item']['feed'] = {}
                    challenge['Item']['feed']['id'] = challenge['Item']['email']
                    challenge['Item']['feed']['key'] = challenge['Item']['creation_time']
                    challenge['Item']['state'] = {}
                    challenge['Item']['state']['S'] = state
                    challenge['Item']['liked'] = {}
                    challenge['Item']['starred'] = {}
                    challenge['Item']['commented'] = {}
                    challenge['Item']['taking_off'] = {}
                    challenge['Item']['taking_off']['BOOL'] = taking_off
                    challenge['Item']['liked']['BOOL'] = liked
                    challenge['Item']['starred']['BOOL'] = starred
                    challenge['Item']['commented']['BOOL'] = commented
                    challenge['Item']['accepted'] = {}
                    challenge['Item']['accepted']['BOOL'] = accepted
                    challenge['Item']['accepted_users'] = {}
                    challenge['Item']['accepted_users']['SS'] = accepted_users_list
                    challenge['Item']['accepted_time'] = {}
                    challenge['Item']['accepted_time']['S'] = ac_time

                    if challenge['Item']['email']['S'] != user_email:
                        following = check_if_user_following_user(user_email,
                                                challenge['Item']['email']['S'])
                        challenge['Item']['user']['following'] = {}
                        challenge['Item']['user']['following']['BOOL'] = following

                    del challenge['Item']['email']
                    del challenge['Item']['value']
                    del challenge['Item']['creation_date']

                    feeds.append(challenge['Item'])

            response['message'] = 'Request successful.'
            response['result'] = feeds
        except:
            response['message'] = 'Request failed. Try again later.'

        return response, 200


class GetUsersProfilePosts(Resource):
    def post(self, user_email):
        """Returns user's posts"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id in user_id.')

        if data.get('last_evaluated_key') == None:
            user_posts = db.query(TableName='posts',
                                Select='ALL_ATTRIBUTES',
                                Limit=50,
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': user_email}
                                }
                            )
        else:
            user_posts = db.query(TableName='posts',
                                Select='ALL_ATTRIBUTES',
                                Limit=50,
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': user_email}
                                },
                                ExclusiveStartKey=data['last_evaluated_key']
                            )

        if user_posts.get('LastEvaluatedKey') != None:
            response['last_evaluated_key'] = user_posts['LastEvaluatedKey']

        try:
            for posts in user_posts['Items']:
                user_name, profile_picture, home = get_user_details(user_email)
                if user_name == None:
                    del posts
                else:
                    feed_id = posts['email']['S'] + '_' + posts['creation_time']['S']
                    liked = check_if_user_liked(feed_id, user_email)
                    starred = check_if_user_starred(feed_id, user_email)
                    commented = check_if_user_commented(feed_id, user_email)
                    taking_off = check_if_taking_off(feed_id, 'posts')
                    added_to_fav = check_if_post_added_to_favorites(feed_id, 
                                                                  user_email)
                    posts['user'] = {}
                    posts['user']['name'] = {}
                    posts['user']['id'] = {}
                    posts['user']['profile_picture'] = {}
                    posts['user']['id']['S'] = user_email
                    posts['user']['name']['S'] = user_name
                    posts['user']['profile_picture']['S'] = profile_picture
                    posts['feed'] = {}
                    posts['feed']['id'] = {}
                    posts['feed']['id']['S'] = posts['email']['S']
                    posts['feed']['key'] = {}
                    posts['feed']['key']['S'] = posts['creation_time']['S']
                    posts['liked'] = {}
                    posts['starred'] = {}
                    posts['commented'] = {}
                    posts['taking_off'] = {}
                    posts['taking_off']['BOOL'] = taking_off
                    posts['liked']['BOOL'] = liked
                    posts['starred']['BOOL'] = starred
                    posts['commented']['BOOL'] = commented
                    posts['added_to_fav'] = {}
                    posts['added_to_fav']['BOOL'] = added_to_fav

                    if posts.get('tags') != None:
                        tags = []
                        for t in posts['tags']['L']:
                            tags.append(t['M'])
                        posts['tags']['L'] = tags

                    if posts['email']['S'] != user_email:
                        following = check_if_user_following_user(user_email,
                                                    posts['email']['S'])
                        posts['user']['following'] = {}
                        posts['user']['following']['BOOL'] = following

                    del posts['email']
                    del posts['value']
            response['message'] = 'Request successful.'
            response['result'] = user_posts['Items']
        except:
            response['message'] = 'Request failed.'

        return response, 200


class GetUsersProfileBadges(Resource):
    def post(self, user_email):
        """Returns user's badges"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id in user_id.')

        badges = []
        response['message'] = 'Request successful.'
        response['result'] = badges

        return response, 200



api.add_resource(UserAccount, '/')
api.add_resource(UserProfilePicture, '/<user_email>/picture')
api.add_resource(UserCommunities, '/<user_email>/communities/<community>')
api.add_resource(UserLogin, '/login')
api.add_resource(ChangePassword, '/<user_email>/password')
api.add_resource(GiveStarsToFollowings, '/stars/share/<user_email>')
api.add_resource(ForgotPassword, '/settings/forgot_password')
profile_api.add_resource(GetUsersStars, '/users/stars/<user_email>')
profile_api.add_resource(GetUsersStarsDetails, 
                          '/users/stars/activity/<user_email>')
profile_api.add_resource(GetUsersProfile, '/users/<user_email>')
profile_api.add_resource(GetUsersProfilePosts, '/users/<user_email>/posts')
profile_api.add_resource(GetUsersProfileChallenges, 
                          '/users/<user_email>/challenges')
profile_api.add_resource(GetUsersProfileFollowings, 
                          '/users/<user_email>/followings')
profile_api.add_resource(GetUsersProfileFollowers, 
                          '/users/<user_email>/followers')
profile_api.add_resource(GetUsersProfileBadges, 
                          '/users/<user_email>/badges')


