import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.helper import (check_if_taking_off, check_if_user_liked,
                    check_if_user_starred, check_if_user_commented,
                    get_user_details, check_challenge_state,
                    check_if_user_exists, check_if_post_added_to_favorites,
                    check_if_challenge_accepted, get_challenge_accepted_users,
                    check_if_user_following_user)

from werkzeug.exceptions import BadRequest

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
        followings = []
        if user['Item'].get('following') != None:
            for following in user['Item']['following']['SS']:
                f = {}
                f['following'] = {}
                f['following']['id'] = {}
                f['following']['name'] = {}
                f['following']['profile_picture'] = {}
                if '@' in following:
                    user_name, profile_picture, home = get_user_details(following)
                    f['following']['home_community'] = {}
                    f['following']['id']['S'] = following
                    f['following']['name']['S'] = user_name
                    f['following']['home_community'] = home
                    f['following']['profile_picture'] = profile_picture
                else:
                    org = db.get_item(TableName='organizations',
                                        Key={'name': {'S': following}})
                    f['following']['type'] = {}
                    f['following']['type']['S'] = 'organization'
                    f['following']['id']['S'] = following
                    f['following']['name']['S'] = following
                    f['following']['profile_picture']['S'] = org['Item']['picture']['S']
                followings.append(f)
            response['message'] = 'Successfully fetched user\'s followings!'
        else:
            response['message'] = 'You have no followings!'
        response['result'] = followings
        return response, 200


    def put(self, user_email):
        """Adds a user or organization to the following and followers list"""
        data = request.get_json(force=True)
        response = {}

        if data['follow'] == None:
            raise BadRequest('Please provide user_id or organization_id ' \
                             + 'in follow.')
        try:
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
            if '@' in data['follow']:
                following_user = check_if_user_exists(data['follow'])
                user_exists = check_if_user_exists(user_email)
                if following_user and user_exists:
                    user = db.update_item(
                                TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='ADD following :following',
                                ExpressionAttributeValues={
                                    ':following': {'SS': [data['follow']]}
                                }
                            )
                    user_following = db.update_item(
                                TableName='users',
                                Key={'email': {'S': data['follow']}},
                                UpdateExpression='ADD followers :follower',
                                ExpressionAttributeValues={
                                    ':follower': {'SS': [user_email]}
                                }
                            )
                    notification = db.put_item(TableName='notifications',
                                Item={'notify_to': {'S': data['follow']},
                                      'creation_time': {'S': date_time},
                                      'email': {'S': user_email},
                                      'from': {'S': 'user'},
                                      'notify_for': {'S': 'following'},
                                      'checked': {'BOOL': False}
                                }
                            )
                    response['message'] = 'Successfully following the user!'
                else:
                    if user_exists == False:
                        response['message'] = 'User does not exist!'
                    if following_user == False:
                        response['message'] = 'The user you are trying to '\
                                              +'follow does not exist!'
            else:
                user = db.update_item(
                            TableName='users',
                            Key={'email': {'S': user_email}},
                            UpdateExpression='ADD following :following',
                            ExpressionAttributeValues={
                                ':following': {'SS': [data['follow']]}
                            }
                        )
                response['message'] = 'Successfully following the organization!'
        except:
            response['message'] = 'Failed to follow user!'
        return response, 200

    def delete(self, user_email):
        """Unfollows a user"""
        data = request.get_json(force=True)
        response = {}

        if data['unfollow'] == None:
            raise BadRequest('Please provide user_id or organization_id ' \
                             + 'to unfollow.')
        try:
            if '@' in data['unfollow']:
                unfollow_user = check_if_user_exists(data['unfollow'])
                user_exists = check_if_user_exists(user_email)
                if unfollow_user and user_exists:
                    user = db.update_item(
                                TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='DELETE following :user',
                                ExpressionAttributeValues={
                                    ':user': {'SS':[data['unfollow']]}
                                }
                            )
                    user_following = db.update_item(
                                TableName='users',
                                Key={'email': {'S': data['unfollow']}},
                                UpdateExpression='DELETE followers :follower',
                                ExpressionAttributeValues={
                                    ':follower': {'SS':[user_email]}
                                }
                            )
                    response['message'] = 'Successfully unfollowed the user.'
                else:
                    if user_exists == False:
                        response['message'] = 'User does not exist!'
                    if unfollow_user == False:
                        response['message'] = 'The user you are trying to '\
                                              +'unfollow does not exist!'
            else:
                user = db.update_item(
                            TableName='users',
                            Key={'email': {'S': user_email}},
                            UpdateExpression='DELETE following :user',
                            ExpressionAttributeValues={
                                ':user': {'SS':[data['unfollow']]}
                            }
                        )
                response['message'] = 'Successfully unfollowed the organization.'
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
                following_follower = check_if_user_following_user(user_email,
                                                                    follower)
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
                f['user']['following'] = {}
                f['user']['following']['BOOL'] = following_follower
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
            response['message'] = 'You have no followings!'
            response['result'] = feeds
        else:
            for user in users_following['Item']['following']['SS']:
                if '@' in user:
                    following_posts = db.query(TableName='posts',
                                       KeyConditionExpression='email = :e',
                                       ExpressionAttributeValues={
                                           ':e': {'S': user}
                                       }
                                   )
                    for post in following_posts['Items']:
                        if post['email']['S'] != user_email:
                            feeds.append(post)

            try:
                for post in feeds:
                    user_name, profile_picture, home = get_user_details(post['email']['S'])
                    if user_name == None:
                        del post
                    else:
                        feed_id = post['email']['S'] + '_' + post['creation_time']['S']
                        liked = check_if_user_liked(feed_id, user_email)
                        starred = check_if_user_starred(feed_id, user_email)
                        commented = check_if_user_commented(feed_id, user_email)
                        taking_off = check_if_taking_off(feed_id, 'posts')
                        added_to_fav = check_if_post_added_to_favorites(feed_id, 
                                                                      user_email)
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

                        if post['email']['S'] != user_email:
                            following = check_if_user_following_user(user_email,
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
            response['message'] = 'You have no followings!'
            response['result'] = feeds
        else:
            for user in users_following['Item']['following']['SS']:
                if '@' in user:
                    following_challenges = db.query(TableName='challenges',
                                       IndexName='challenges-creator-key',
                                       KeyConditionExpression='creator = :e',
                                       ExpressionAttributeValues={
                                           ':e': {'S': user}
                                       }
                                   )
                    
                    for feed in following_challenges['Items']:
                        if feed['creator']['S'] != user_email:
                            feeds.append(feed)

            try:
                for challenge in feeds:
                    user_name, profile_picture, home = get_user_details(challenge['creator']['S'])
                    if user_name == None:
                        del challenge
                    else:
                        feed_id = challenge['creator']['S'] + '_' + challenge['creation_key']['S']
                        liked = check_if_user_liked(feed_id, user_email)
                        starred = check_if_user_starred(feed_id, user_email)
                        commented = check_if_user_commented(feed_id, user_email)
                        # state = check_challenge_state(challenge['email']['S'], challenge['creation_time']['S'])
                        taking_off = check_if_taking_off(feed_id, 'challenges')
                        challenge_accepted, c_state = check_if_challenge_accepted(
                                                              feed_id, user_email)
                        accepted_users_list = get_challenge_accepted_users(
                                                       feed_id, user_email)
                        challenge['user'] = {}
                        challenge['user']['id'] = challenge['creator']
                        challenge['user']['name'] = {}
                        challenge['user']['profile_picture'] = {}
                        challenge['user']['name']['S'] = user_name
                        challenge['user']['profile_picture']['S'] = profile_picture
                        challenge['feed'] = {}
                        challenge['feed']['id'] = challenge['creator']
                        challenge['feed']['key'] = challenge['creation_key']
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

                        if challenge['creator']['S'] != user_email:
                            following = check_if_user_following_user(user_email,
                                                    challenge['creator']['S'])
                            challenge['user']['following'] = {}
                            challenge['user']['following']['BOOL'] = following

                        del challenge['email']
                        del challenge['creator']
                        del challenge['value']
                        del challenge['creation_key']
                response['message'] = 'Successfully fetched all following\'s challenges!'
                response['results'] = feeds
            except:
                response['message'] = 'Failed to fetch following\'s challenges!'
        return response, 200


api.add_resource(UserFollowings, '/<user_email>/following')
api.add_resource(UserFollowers, '/<user_email>/followers')
api.add_resource(UserFollowingPostsFeeds, '/following/posts/<user_email>')
api.add_resource(UserFollowingChallengesFeeds, '/following/challenges/<user_email>')
