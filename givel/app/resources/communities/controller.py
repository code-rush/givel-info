import boto3

from app.app import app

from flask import Blueprint, request, json
from flask_restful import Resource, Api

from app.models import create_community_table

from app.helper import check_if_taking_off, check_if_user_liked
from app.helper import check_if_user_starred, check_if_user_commented
from app.helper import get_user_details, check_challenge_state
from app.helper import check_if_challenge_accepted, get_challenge_accepted_users
from app.helper import check_if_post_added_to_favorites


db = boto3.client('dynamodb')

try:
    try:
        table_response = db.describe_table(TableName='communities')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('Communities Table exists!')
    except:
        communities = create_community_table()
        print('Communities table created!')
except:
    pass


community_api_routes = Blueprint('community_api', __name__)
api = Api(community_api_routes)


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


class Communities(Resource):
    def get(self):
        """Returns all communities"""
        communities = db.scan(TableName='communities')
        items = communities['Items']
        response = {}
        for i in items:
            i['state']['S'] = STATES[i['state']['S']]
        response['message'] = 'Success!'
        response['results'] = items
        return response, 200

class CommunityPosts(Resource):
    def get(self, user_email):
        """Returns all posts from users communities"""
        response = {}
        user_communities = db.get_item(TableName='users',
                               Key={'email': {'S': user_email}},
                               ProjectionExpression='home, home_away'
                           )
        users = []
        home_users = db.query(TableName='users',
                            IndexName='users-in-home-community',
                            KeyConditionExpression='home = :h',
                            ExpressionAttributeValues={
                                ':h': {'S': user_communities['Item']['home']['S']}
                            }
                        )
        users = home_users['Items']

        if user_communities['Item'].get('home_away') != None:
            home_away_users = db.query(TableName='users',
                                IndexName='users-in-home-away-community',
                                KeyConditionExpression='home_away = :h',
                                ExpressionAttributeValues={
                                    ':h': {'S': user_communities['Item']['home_away']['S']}
                                }
                            )

            users = users + home_away_users['Items']

        feeds = []
        for user in users:
            try:
                community_posts = db.query(TableName='posts',
                                       KeyConditionExpression='email = :e',
                                       ExpressionAttributeValues={
                                           ':e': {'S': user['email']['S']}
                                       }
                                   )
                for post in community_posts['Items']:
                    user_name, profile_picture, home = get_user_details(post['email']['S'])
                    if user_name == None:
                        del post
                    else:
                        feed_id = post['email']['S'] + '_' + post['creation_time']['S']
                        liked = check_if_user_liked(feed_id, user_email)
                        starred = check_if_user_starred(feed_id, user_email)
                        commented = check_if_user_commented(feed_id, user_email)
                        taking_off = check_if_taking_off(feed_id, 'posts')
                        added_to_fav = check_if_post_added_to_favorites(
                                        feed_id, user_email)
                        post['user'] = {}
                        post['user']['id'] = post['email']
                        post['user']['name'] = {}
                        post['user']['profile_picture'] = {}
                        post['user']['name']['S'] = user_name
                        post['user']['profile_picture']['S'] = profile_picture
                        post['feed'] = {}
                        post['feed']['id'] = post['email']
                        post['feed']['key'] = post['creation_time']
                        post['liked'] = {}
                        post['starred'] = {}
                        post['commented'] = {}
                        post['taking_off'] = {}
                        post['taking_off']['BOOL'] = taking_off
                        post['liked']['BOOL'] = liked
                        post['starred']['BOOL'] = starred
                        post['commented']['BOOL'] = commented
                        post['added_to_fav'] = {}
                        post['added_to_fav']['BOOL'] = added_to_fav
                        del post['email']
                        del post['value']
                        feeds.append(post)
                response['message'] = 'Successfully fetched all community posts!'
                response['results'] = feeds
            except:
                response['message'] = 'Failed to fetch community posts!'

        return response, 200


class CommunityChallenges(Resource):
    def get(self, user_email):
        """Returns all challenges in users community"""
        response = {}
        user_communities = db.get_item(TableName='users',
                               Key={'email': {'S': user_email}},
                               ProjectionExpression='home, home_away'
                           )
        users = []
        home_users = db.query(TableName='users',
                            IndexName='users-in-home-community',
                            KeyConditionExpression='home = :h',
                            ExpressionAttributeValues={
                                ':h': {'S': user_communities['Item']['home']['S']}
                            }
                        )
        users = home_users['Items']

        if user_communities['Item'].get('home_away') != None:
            home_away_users = db.query(TableName='users',
                                IndexName='users-in-home-away-community',
                                KeyConditionExpression='home_away = :h',
                                ExpressionAttributeValues={
                                    ':h': {'S': user_communities['Item']['home_away']['S']}
                                }
                            )
            users = users + home_away_users['Items']
            

        feeds = []
        for user in users:
            try:
                community_challenges = db.query(TableName='challenges',
                                       KeyConditionExpression='email = :e',
                                       ExpressionAttributeValues={
                                           ':e': {'S': user['email']['S']}
                                       }
                                   )
                for challenge in community_challenges['Items']:
                    user_name, profile_picture, home = get_user_details(challenge['creator']['S'])
                    if user_name == None:
                        del challenge
                    else:
                        feed_id = challenge['email']['S'] + '_' + challenge['creation_time']['S']
                        liked = check_if_user_liked(feed_id, user_email)
                        starred = check_if_user_starred(feed_id, user_email)
                        commented = check_if_user_commented(feed_id, user_email)
                        state = check_challenge_state(challenge['email']['S'], challenge['creation_time']['S'])
                        taking_off = check_if_taking_off(feed_id, 'challenges')
                        challenge_accepted, c_state = check_if_challenge_accepted(feed_id,
                                              user_email, challenge['creator']['S'],
                                              challenge['creation_key']['S'])
                        accepted_users_list = get_challenge_accepted_users(
                                            challenge['creator']['S'], 
                                            challenge['creation_key']['S'],
                                            challenge['email']['S'])
                        challenge['user'] = {}
                        challenge['user']['name'] = {}
                        challenge['user']['id'] = challenge['email']
                        challenge['user']['profile_picture'] = {}
                        challenge['user']['name']['S'] = user_name
                        challenge['user']['profile_picture']['S'] = profile_picture
                        challenge['feed'] = {}
                        challenge['feed']['id'] = challenge['email']
                        challenge['feed']['key'] = challenge['creation_time']
                        challenge['state'] = {}
                        if c_state == None:
                            challenge['state']['S'] = state
                        else:
                            challenge['state']['S'] = c_state
                        challenge['liked'] = {}
                        challenge['starred'] = {}
                        challenge['commented'] = {}
                        challenge['taking_off'] = {}
                        challenge['taking_off']['BOOL'] = taking_off
                        challenge['liked']['BOOL'] = liked
                        challenge['starred']['BOOL'] = starred
                        challenge['commented']['BOOL'] = commented
                        challenge['accepted'] = {}
                        challenge['accepted']['BOOL'] = challenge_accepted
                        challenge['accepted_users'] = {}
                        challenge['accepted_users']['SS'] = accepted_users_list 
                        del challenge['email']
                        del challenge['creator']
                        del challenge['value']
                        del challenge['creation_key']
                        feeds.append(challenge)
                response['message'] = 'Successfully fetched all community challenges!'
                response['results'] = feeds
            except:
                response['message'] = 'Failed to fetch users challenges!'
        return response, 200


api.add_resource(Communities, '/')
api.add_resource(CommunityPosts, '/posts/<user_email>')
api.add_resource(CommunityChallenges, '/challenges/<user_email>')

