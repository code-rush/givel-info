import boto3
import datetime
import string
import random

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
                        check_challenge_state, check_if_user_commented)


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
                                 'total_stars_shared': {'N': '0'},
                                 'following': {'SS': ['greg@givel.co']}
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


class GetUsersProfile(Resource):
    def post(self, user_email):
        """Returns user's profile"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user_id.')
        else:
            user_profile = db.get_item(TableName='users',
                            Key={'email': {'S':data['user_id']}})

            user_following = check_if_user_following_user(user_email, 
                                                      data['user_id'])
            name, picture, home = get_user_details(data['user_id'])

            profile_details = {}

            if user_profile['Item'] != None:
                followings = []
                followers = []
                if user_profile['Item'].get('following') != None:
                    for following in user_profile['Item']['following']['SS']:
                        user_name, profile_picture, home = get_user_details(following)
                        following_following = check_if_user_following_user(user_email,
                                                                            following)
                        user_profile['followings'] = {}
                        user_profile['followings']['id'] = {}
                        user_profile['followings']['name'] = {}
                        user_profile['followings']['following'] = {}
                        user_profile['followings']['profile_picture'] = {}
                        user_profile['followings']['home_community'] = {}
                        user_profile['followings']['id']['S'] = following
                        user_profile['followings']['name']['S'] = user_name
                        user_profile['followings']['following']['BOOL'] = following_following
                        user_profile['followings']['profile_picture']['S'] = profile_picture
                        user_profile['followings']['home_community']['S'] = home
                        followings.append(user_profile['followings'])

                if user_profile['Item'].get('followers') != None:
                    for follower in user_profile['Item']['followers']['SS']:
                        user_name, profile_picture, home = get_user_details(follower)
                        following_follower = check_if_user_following_user(user_email, 
                                                                            follower)
                        user_profile['follower'] = {}
                        user_profile['follower']['id'] = {}
                        user_profile['follower']['name'] = {}
                        user_profile['follower']['following'] = {}
                        user_profile['follower']['profile_picture'] = {}
                        user_profile['follower']['home_community'] = {}
                        user_profile['follower']['id']['S'] = follower
                        user_profile['follower']['name']['S'] = user_name
                        user_profile['follower']['following']['BOOL'] = following_follower
                        user_profile['follower']['profile_picture']['S'] = profile_picture
                        user_profile['follower']['home_community']['S'] = home
                        followers.append(user_profile['follower'])

                badges = []

                posts = db.query(TableName='posts',
                            Select='ALL_ATTRIBUTES',
                            Limit=50,
                            KeyConditionExpression='email = :e',
                            ExpressionAttributeValues={
                                ':e': {'S': data['user_id']}
                            }
                        )

                users_posts = []
                for post in posts['Items']:
                    user_name, profile_picture, home = get_user_details(data['user_id'])
                    feed_id = post['email']['S'] + '_' + post['creation_time']['S']
                    liked = check_if_user_liked(feed_id, user_email)
                    starred = check_if_user_starred(feed_id, user_email)
                    commented = check_if_user_commented(feed_id, user_email)
                    taking_off = check_if_taking_off(feed_id, 'posts')
                    post['user'] = {}
                    post['user']['name'] = {}
                    post['user']['id'] = {}
                    post['user']['profile_picture'] = {}
                    post['user']['id']['S'] = data['user_id']
                    post['user']['name']['S'] = user_name
                    post['user']['profile_picture']['S'] = profile_picture
                    post['feed'] = {}
                    post['feed']['id'] = {}
                    post['feed']['id']['S'] = post['email']['S']
                    post['feed']['key'] = {}
                    post['feed']['key']['S'] = post['creation_time']['S']
                    post['liked'] = {}
                    post['starred'] = {}
                    post['commented'] = {}
                    post['taking_off'] = {}
                    post['taking_off']['BOOL'] = taking_off
                    post['liked']['BOOL'] = liked
                    post['starred']['BOOL'] = starred
                    post['commented']['BOOL'] = commented
                    del post['email']
                    del post['value']
                    users_posts.append(post)

                
                challenges = db.query(TableName='challenges',
                                Select='ALL_ATTRIBUTES',
                                Limit=50,
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': data['user_id']}
                                }
                            )

                users_challenges = []
                for challenge in challenges['Items']:
                    user_name, profile_picture, home = get_user_details(
                                                challenge['creator']['S'])
                    feed_id = challenge['email']['S'] + '_' \
                              + challenge['creation_time']['S']
                    liked = check_if_user_liked(feed_id, user_email)
                    starred = check_if_user_starred(feed_id, user_email)
                    commented = check_if_user_commented(feed_id, user_email)
                    state = check_challenge_state(challenge['email']['S'],
                                            challenge['creation_time']['S'])
                    taking_off = check_if_taking_off(feed_id, 'challenges')
                    challenge['user'] = {}
                    challenge['user']['name'] = {}
                    challenge['user']['profile_picture'] = {}
                    challenge['user']['id'] = challenge['creator']
                    challenge['user']['name']['S'] = user_name
                    challenge['user']['profile_picture']['S'] = profile_picture
                    challenge['feed'] = {}
                    challenge['feed']['id'] = challenge['email']
                    challenge['feed']['key'] = challenge['creation_time']
                    challenge['state'] = {}
                    challenge['state']['S'] = state
                    challenge['liked'] = {}
                    challenge['starred'] = {}
                    challenge['commented'] = {}
                    challenge['taking_off'] = {}
                    challenge['taking_off']['BOOL'] = taking_off
                    challenge['liked']['BOOL'] = liked
                    challenge['starred']['BOOL'] = starred
                    challenge['commented']['BOOL'] = commented
                    del challenge['email']
                    del challenge['creator']
                    del challenge['value']
                    users_challenges.append(challenge)

                profile_details['followers'] = {}
                profile_details['followers']['SS'] = followers
                profile_details['followings'] = {}
                profile_details['followings']['SS'] = followings
                profile_details['badges'] = {}
                profile_details['badges']['SS'] = badges
                profile_details['user'] = {}
                profile_details['user']['name'] = {}
                profile_details['user']['name']['S'] = name
                profile_details['user']['profile_picture'] = {}
                profile_details['user']['profile_picture']['S'] = picture
                profile_details['user']['home_community'] = {}
                profile_details['user']['home_community']['S'] = home
                profile_details['user']['following'] = {}
                profile_details['user']['following']['BOOL'] = user_following
                profile_details['posts'] = {}
                profile_details['challenges'] = {}
                profile_details['posts']['SS'] = users_posts
                profile_details['challenges']['SS'] = users_challenges

                response['message'] = 'Request successful!'
                response['result'] = profile_details
            else:
                response['message'] = 'User not found!'

            return response, 200


api.add_resource(UserAccount, '/')
api.add_resource(UserProfilePicture, '/<user_email>/picture')
api.add_resource(UserCommunities, '/<user_email>/communities/<community>')
api.add_resource(UserLogin, '/login')
api.add_resource(ChangePassword, '/<user_email>/password')
api.add_resource(GiveStarsToFollowings, '/stars/share/<user_email>')
api.add_resource(ForgotPassword, '/settings/forgot_password')
profile_api.add_resource(GetUsersProfile, '/users/<user_email>')

