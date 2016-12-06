import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.helper import check_if_taking_off, check_if_user_liked
from app.helper import check_if_user_starred, check_if_user_commented
from app.helper import get_user_details, check_challenge_state

user_following_activity_api_routes = Blueprint('following_activity_api', __name__)
api = Api(user_following_activity_api_routes)

db = boto3.client('dynamodb')


class UserFollowings(Resource):
    def get(self, user_email):
        """Returns list of users followings"""
        response = {}
        user = db.get_item(
                    TableName='users',
                    Key={'email': {'S': user_email}}
                )
        if user['Item'].get('following') != None:
            followings = []
            for following in user['Item']['following']['SS']:
                user_name, profile_picture, home = get_user_details(following)
                f = {}
                f['user'] = {}
                f['user']['id'] = {}
                f['user']['name'] = {}
                f['user']['home_community'] = {}
                f['user']['profile_picture'] = {}
                f['user']['id']['S'] = following
                f['user']['name']['S'] = user_name
                f['user']['home_community'] = home
                f['user']['profile_picture'] = profile_picture
                followings.append(f)
            response['message'] = 'Success!'
            response['result'] = followings
        else:
            response['message'] = 'Success!'
            response['result'] = 'You have no followings!'
        return response, 200


    def put(self, user_email):
        """Adds a user to the following and followers list"""
        data = request.get_json(force=True)
        response = {}
        try:
            if data['follow_user']:
                user = db.update_item(
                            TableName='users',
                            Key={'email': {'S': user_email}},
                            UpdateExpression='ADD following :following',
                            ExpressionAttributeValues={
                                ':following': {'SS': [data['follow_user']]}
                            },
                            ReturnValues='UPDATED_NEW'
                        )
                user_following = db.update_item(
                            TableName='users',
                            Key={'email': {'S': data['follow_user']}},
                            UpdateExpression='ADD followers :follower',
                            ExpressionAttributeValues={
                                ':follower': {'SS': [user_email]}
                            }
                        )
                response['message'] = 'Successfully following the user!'
                response['result'] = user['Attributes']
        except:
            response['message'] = 'Failed to follow user!'
        return response, 200

    def delete(self, user_email):
        """Unfollows a user"""
        data = request.get_json(force=True)
        response = {}
        try:
            if data['unfollow_user']:
                user = db.update_item(
                            TableName='users',
                            Key={'email': {'S': user_email}},
                            UpdateExpression='DELETE following :user',
                            ExpressionAttributeValues={
                                ':user': {'SS':[data['unfollow_user']]}
                            },
                            ReturnValues='UPDATED_NEW'
                        )
                user_following = db.update_item(
                            TableName='users',
                            Key={'email': {'S': data['unfollow_user']}},
                            UpdateExpression='DELETE followers :follower',
                            ExpressionAttributeValues={
                                ':follower': {'SS':[user_email]}
                            }
                        )
                response['message'] = 'Success! You unfollowed the user.'
                if user.get('Attributes') != None:
                    response['result'] = user['Attributes']
                else:
                    response['result'] = 'You have no Followings!'
        except:
            response['message'] = 'Request Failed.'
        return response, 200


class UserFollowers(Resource):
    def get(self, user_email):
        """Returns list of followers"""
        response = {}
        user = db.get_item(
                        TableName='users',
                        Key={'email': {'S': user_email}}
                    )
        if user['Item'].get('followers') != None:
            followers = []
            for follower in user['Item']['followers']['SS']:
                user_name, profile_picture, home = get_user_details(follower)
                f = {}
                f['user'] = {}
                f['user']['name'] = {}
                f['user']['id'] = {}
                f['user']['home_community'] = {}
                f['user']['profile_picture'] = {}
                f['user']['name']['S'] = user_name
                f['user']['id']['S'] = follower
                f['user']['home_community'] = home
                f['user']['profile_picture'] = profile_picture
                followers.append(f)
            response['message'] = 'Success!'
            response['result'] = followers
        else:
            response['message'] = 'Success!'
            response['message'] = 'You have no followers!'
        return response, 200


class UserFollowingPostsFeeds(Resource):
    def get(self, user_email):
        """Returns users followings all posts"""
        response = {}
        users_following = db.get_item(TableName='users',
                            Key={'email': {'S': user_email}}
                        )
        feeds = []
        if users_following['Item'].get('following') == None:
            response['message'] = 'Success!'
            response['result'] = 'You are not following any user!'
        else:
            for user in users_following['Item']['following']['SS']:
                try:
                    following_posts = db.query(TableName='posts',
                                           KeyConditionExpression='email = :e',
                                           ExpressionAttributeValues={
                                               ':e': {'S': user}
                                           }
                                       )
                    for post in following_posts['Items']:
                        user_name, profile_picture, home = get_user_details(post['email']['S'])
                        if user_name == None:
                            del post
                        else:
                            feed_id = post['email']['S'] + '_' + post['creation_time']['S']
                            liked = check_if_user_liked(feed_id, user_email)
                            starred = check_if_user_starred(feed_id, user_email)
                            commented = check_if_user_commented(feed_id, user_email)
                            taking_off = check_if_taking_off(feed_id, 'posts')
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
                            del post['email']
                            del post['value']
                            feeds.append(post)
                    response['message'] = 'Successfully fetched all following posts!'
                    response['results'] = feeds
                except:
                    response['message'] = 'Failed to fetch following posts!'

        return response, 200


class UserFollowingChallengesFeeds(Resource):
    def get(self, user_email):
        """Returns users followings challenges feed"""
        response = {}
        users_following = db.get_item(TableName='users',
                            Key={'email': {'S': user_email}}
                        )
        feeds = []
        if users_following['Item'].get('following') == None:
            response['message'] = 'Success!'
            response['result'] = 'You are not following any user!'
        else:
            for user in users_following['Item']['following']['SS']:
                try:
                    community_challenges = db.query(TableName='challenges',
                                           KeyConditionExpression='email = :e',
                                           ExpressionAttributeValues={
                                               ':e': {'S': user}
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
                            challenge['user'] = {}
                            challenge['user']['id'] = challenge['email']
                            challenge['user']['name'] = {}
                            challenge['user']['profile_picture'] = {}
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
                            feeds.append(challenge)
                    response['message'] = 'Successfully fetched all following\'s challenges!'
                    response['results'] = feeds
                except:
                    response['message'] = 'Failed to fetch following\'s challenges!'
        return response, 200


api.add_resource(UserFollowings, '/<user_email>/following')
api.add_resource(UserFollowers, '/<user_email>/followers')
api.add_resource(UserFollowingPostsFeeds, '/following/posts/<user_email>')
api.add_resource(UserFollowingChallengesFeeds, '/following/challenges/<user_email>')
