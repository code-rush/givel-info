import boto3

from app.app import app

from flask import Blueprint, request, json
from flask_restful import Resource, Api

from app.models import create_community_table

from app.helper import (check_if_taking_off, check_if_user_liked,
                        check_if_user_starred, check_if_user_commented,
                        get_user_details, check_challenge_state,
                        check_if_challenge_accepted, 
                        get_challenge_accepted_users,
                        check_if_post_added_to_favorites,
                        check_if_user_following_user, get_feeds,
                        check_if_user_exists)


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


class Communities(Resource):
    def get(self):
        """Returns all communities"""
        communities = db.scan(TableName='communities')
        items = communities['Items']
        response = {}
        response['message'] = 'Success!'
        response['results'] = items
        return response, 200

class CommunityPosts(Resource):
    def post(self):
        """Returns all posts from users communities"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id.')

        user_exists = check_if_user_exists(data['user_id'])

        if not user_exists:
            raise BadRequest('User does not exist.')

        user_communities = db.get_item(TableName='users',
                               Key={'email': {'S': data['user_id']}},
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
        for user in home_users['Items']:
            users.append(user['email']['S'])

        if user_communities['Item'].get('home_away') != None:
            home_away_users = db.query(TableName='users',
                                IndexName='users-in-home-away-community',
                                KeyConditionExpression='home_away = :h',
                                ExpressionAttributeValues={
                                    ':h': {'S': user_communities['Item']['home_away']['S']}
                                }
                            )

            for user in home_away_users['Items']:
                if user['email']['S'] not in users:
                    users.append(user['email']['S'])

        for user in users:
            following = check_if_user_following_user(data['user_id'], user)
            if following:
                users.remove(user)

        if data['user_id'] in users:
            users.remove(data['user_id'])

        feeds = []

        if data.get('last_evaluated_key') == None:
            community_feeds, last_evaluated_key = get_feeds(
                                            users, 'posts')
        else:
            community_feeds, last_evaluated_key = get_feeds(users, 
                                    'posts', data['last_evaluated_key'])

        if last_evaluated_key != None:
            response['last_evaluated_key'] = last_evaluated_key

        try:
            for post in community_feeds:
                user_name, profile_picture, home = get_user_details(post['email']['S'])
                if user_name == None:
                    del post
                else:
                    feed_id = post['email']['S'] + '_' + post['creation_time']['S']
                    liked = check_if_user_liked(feed_id, data['user_id'])
                    starred = check_if_user_starred(feed_id, data['user_id'])
                    commented = check_if_user_commented(feed_id, data['user_id'])
                    taking_off = check_if_taking_off(feed_id, 'posts')
                    added_to_fav = check_if_post_added_to_favorites(
                                    feed_id, data['user_id'])
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

                    if post['email']['S'] != data['user_id']:
                        following = check_if_user_following_user(data['user_id'],
                                                     post['email']['S'])
                        post['user']['following'] = {}
                        post['user']['following']['BOOL'] = following

                    if post.get('tags') != None:
                        tags = []
                        for t in post['tags']['L']:
                            tags.append(t['M'])
                        post['tags']['L'] = tags

                    del post['email']
                    del post['value']
                    del post['creation_date']

                    feeds.append(post)

            response['message'] = 'Request successful.'
            response['results'] = feeds
        except:
            response['message'] = 'Request failed. Please try again later.'

        return response, 200


class CommunityChallenges(Resource):
    def post(self):
        """Returns all challenges in users community"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id.')

        user_exists = check_if_user_exists(data['user_id'])

        if not user_exists:
            raise BadRequest('User does not exist.')

        user_communities = db.get_item(TableName='users',
                               Key={'email': {'S': data['user_id']}},
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

        for user in home_users['Items']:
            users.append(user['email']['S'])

        if user_communities['Item'].get('home_away') != None:
            home_away_users = db.query(TableName='users',
                                IndexName='users-in-home-away-community',
                                KeyConditionExpression='home_away = :h',
                                ExpressionAttributeValues={
                                    ':h': {'S': user_communities['Item']['home_away']['S']}
                                }
                            )
            for user in home_away_users['Items']:
                if user['email']['S'] not in users:
                    users.append(user['email']['S'])

        for user in users:
            following = check_if_user_following_user(data['user_id'], user)
            if following:
                users.remove(user)

        if data['user_id'] in users:
            users.remove(data['user_id'])

        feeds = []

        if data.get('last_evaluated_key') == None:
            community_feeds, last_evaluated_key = get_feeds(
                                            users, 'challenges')
        else:
            community_feeds, last_evaluated_key = get_feeds(users, 
                                    'challenges', data['last_evaluated_key'])

        if last_evaluated_key != None:
            response['last_evaluated_key'] = last_evaluated_key

        try:
            for challenge in community_feeds:
                user_name, profile_picture, home = get_user_details(challenge['creator']['S'])
                if user_name == None:
                    del challenge
                else:
                    feed_id = challenge['creator']['S'] + '_' + challenge['creation_key']['S']
                    liked = check_if_user_liked(feed_id, data['user_id'])
                    starred = check_if_user_starred(feed_id, data['user_id'])
                    commented = check_if_user_commented(feed_id, data['user_id'])
                    # state = check_challenge_state(challenge['email']['S'], challenge['creation_time']['S'])
                    taking_off = check_if_taking_off(feed_id, 'challenges')
                    challenge_accepted, c_state = check_if_challenge_accepted(
                                                        feed_id, data['user_id'])
                    accepted_users_list = get_challenge_accepted_users(
                                                  feed_id, data['user_id'])

                    if challenge_accepted == True:
                        challenge['accepted_time'] = challenge['creation_time']
                    challenge['user'] = {}
                    challenge['user']['name'] = {}
                    challenge['user']['id'] = challenge['creator']
                    challenge['user']['profile_picture'] = {}
                    challenge['user']['name']['S'] = user_name
                    challenge['user']['profile_picture']['S'] = profile_picture
                    challenge['feed'] = {}
                    challenge['feed']['id'] = challenge['creator']
                    challenge['feed']['key'] = challenge['creation_key']
                    if c_state != None:
                        challenge['state'] = {}
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
                    challenge['creation_time'] = challenge['creation_key']


                    if challenge['creator']['S'] != data['user_id']:
                        following = check_if_user_following_user(data['user_id'],
                                                challenge['creator']['S'])
                        challenge['user']['following'] = {}
                        challenge['user']['following']['BOOL'] = following

                    del challenge['email']
                    del challenge['creator']
                    del challenge['value']
                    del challenge['creation_key']
                    del challenge['creation_date']

                    if challenge_accepted and (c_state == 'INACTIVE' \
                      or c_state == 'COMPLETE'):
                        del challenge
                    else:
                        feeds.append(challenge)

            response['message'] = 'Request successful.'
            response['results'] = feeds
        except:
            response['message'] = 'Request failed. Please try again later.'

        return response, 200


api.add_resource(Communities, '/')
api.add_resource(CommunityPosts, '/posts')
api.add_resource(CommunityChallenges, '/challenges')

