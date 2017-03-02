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
                    check_if_user_following_user, get_feeds,
                    update_notifications_activity_page)

from app.models import create_following_activity_table

from werkzeug.exceptions import BadRequest

user_following_activity_api_routes = Blueprint('following_activity_api', __name__)
api = Api(user_following_activity_api_routes)

db = boto3.client('dynamodb')


try:
    try:
        table_response = db.describe_table(TableName='following_activity')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('following_activity Table exists!')
    except:
        following_activity = create_following_activity_table()
        print('following_activity Table created!')
except:
    pass


class GetUsersFollowings(Resource):
    def post(self):
        """Returns list of user's followings"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id.')

        user_exists = check_if_user_exists(data['user_id'])
        if not user_exists:
            raise BadRequest('User does not exist.')

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

            if users.get('Items') != None:
                for following in users['Items']:
                    f = {}
                    f['following'] = {}
                    f['following']['id'] = {}
                    f['following']['name'] = {}
                    if following['type']['S'] == 'user':
                        following_user_exists = check_if_user_exists(
                                                following['id2']['S'])
                        if following_user_exists:
                            user_name, photo, home = get_user_details(
                                                   following['id2']['S'])
                            f['following']['home_community'] = {}
                            f['following']['id']['S'] = following['id2']['S']
                            f['following']['name']['S'] = user_name
                            f['following']['home_community']['S'] = home
                            f['following']['type'] = {}
                            f['following']['type']['S'] = 'user'
                            if photo != None:
                                f['following']['profile_picture'] = {}
                                f['following']['profile_picture']['S'] = photo
                            followings.append(f)
                    else:
                        org = db.get_item(TableName='organizations',
                            Key={'name': {'S': following['id2']['S']}})

                        if org.get('Item') != None:
                            f['following']['type'] = {}
                            f['following']['type']['S'] = 'organization'
                            f['following']['id']['S'] = following['id2']['S']
                            f['following']['name']['S'] = org['Item']\
                                                              ['name']['S']
                            f['following']['profile_picture'] = org['Item']\
                                                                  ['picture']
                            followings.append(f)

            if users.get('LastEvaluatedKey') != None:
                response['last_evaluated_key'] = users['LastEvaluatedKey']

            response['message'] = 'Request successful.'
            response['result'] = followings
        except:
            response['message'] = 'Request failed. Try again later.'

        return response, 200         



class UserFollowings(Resource):
    def put(self, user_email):
        """Adds a user or organization to the following and followers list"""
        data = request.get_json(force=True)
        response = {}

        user_exists = check_if_user_exists(user_email)

        if not user_exists:
            raise BadRequest('User does not exist!')
        if data['follow'] == None:
            raise BadRequest('Please provide user\'s id or ' \
                                + 'organization\'s id')
        if user_email == data['follow']:
            raise BadRequest('Users cannot follow themselves.')

        try:
            date_time = datetime.datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S:%f")
            if '@' in data['follow']:
                following_user_exists = check_if_user_exists(data['follow'])
                if following_user_exists:
                    following_activity = db.get_item(
                                        TableName='following_activity',
                                        Key={'id1': {'S': user_email},
                                             'id2': {'S': data['follow']}
                                        }
                                    )
                    if following_activity.get('Item') != None:
                        add_following = db.update_item(
                                    TableName='following_activity',
                                    Key={'id1': {'S': user_email},
                                         'id2': {'S': data['follow']}
                                    },
                                    UpdateExpression='SET following = :f',
                                    ExpressionAttributeValues={
                                        ':f': {'S': 'True'}
                                    }
                                )
                        add_follower = db.update_item(
                                    TableName='following_activity',
                                    Key={'id2': {'S': user_email},
                                         'id1': {'S': data['follow']}
                                    },
                                    UpdateExpression='SET follower = :f',
                                    ExpressionAttributeValues={
                                        ':f': {'S': 'True'}
                                    }
                                )
                    else:
                        add_following = db.put_item(
                                    TableName='following_activity',
                                    Item={'id1': {'S': user_email},
                                          'id2': {'S': data['follow']},
                                          'type': {'S': 'user'},
                                          'following': {'S': 'True'},
                                          'follower': {'S': 'False'}
                                    }
                                )
                        add_follower = db.put_item(
                                    TableName='following_activity',
                                    Item={'id2': {'S': user_email},
                                          'id1': {'S': data['follow']},
                                          'type': {'S': 'user'},
                                          'following': {'S': 'False'},
                                          'follower': {'S': 'True'}
                                    }
                                )

                    notification = db.put_item(TableName='notifications',
                                Item={'notify_to': {'S': data['follow']},
                                      'creation_time': {'S': date_time},
                                      'email': {'S': user_email},
                                      'from': {'S': 'user'},
                                      'notify_for': {'S': 'following'},
                                      'checked': {'BOOL': True}
                                }
                            )
                    update_notifications_activity_page(data['follow'], False)
                else:
                    response['message'] = 'User you are trying ' \
                                            +'to follow does not exist.'
            else:
                add_following = db.put_item(
                                TableName='following_activity',
                                Item={'id1': {'S': user_email},
                                      'id2': {'S': data['follow']},
                                      'type': {'S': 'organization'},
                                      'following': {'S': 'True'}
                                }
                            )
            response['message'] = 'Request successful.'
        except:
            response['message'] = 'Request failed. Try again later.'

        return response, 200


    def delete(self, user_email):
        """Unfollows a user"""
        data = request.get_json(force=True)
        response = {}

        user_exists = check_if_user_exists(user_email)

        if not user_exists:
            raise BadRequest('User does not exist!')
        if data['unfollow'] == None:
            raise BadRequest('Please provide user\'s id or ' \
                                + 'organization\'s id')

        try:
            if '@' in data['unfollow']:
                activity = db.get_item(TableName='following_activity',
                                        Key={'id1': {'S': user_email},
                                             'id2': {'S': data['unfollow']}
                                        }
                                    )
                if activity['Item']['following']['S'] == 'True'\
                  and activity['Item']['follower']['S'] == 'True':
                    delete_following = db.update_item(
                                        TableName='following_activity',
                                        Key={'id1': {'S': user_email},
                                             'id2': {'S': data['unfollow']}
                                        },
                                        UpdateExpression='SET following = :f',
                                        ExpressionAttributeValues={
                                            ':f': {'S': 'False'}
                                        }
                                    )
                    delete_follower = db.update_item(
                                        TableName='following_activity',
                                        Key={'id2': {'S': user_email},
                                             'id1': {'S': data['unfollow']}
                                        },
                                        UpdateExpression='SET follower = :f',
                                        ExpressionAttributeValues={
                                            ':f': {'S': 'False'}
                                        }
                                    )
                else:
                    delete_following = db.delete_item(
                                        TableName='following_activity',
                                        Key={'id1': {'S': user_email},
                                             'id2': {'S': data['unfollow']}
                                        }
                                    )
                    delete_follower = db.delete_item(
                                        TableName='following_activity',
                                        Key={'id1': {'S': data['unfollow']},
                                             'id2': {'S': user_email}
                                        }
                                    )
            else:
                delete_following = db.delete_item(TableName='following_activity',
                                        Key={'id1': {'S': user_email},
                                             'id2': {'S': data['unfollow']}
                                        }
                                    )
            response['message'] = 'Request successful.'
        except:
            response['message'] = 'Request failed. Try again later.'

        return response, 200


class GetUsersFollowers(Resource):
    def post(self):
        """Returns list of user's followers"""

        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id.')

        user_exists = check_if_user_exists(data['user_id'])
        if not user_exists:
            raise BadRequest('User does not exist.')

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

            if users.get('Items') != None:
                for follower in users['Items']:
                    follower_exists = check_if_user_exists(
                                            follower['id1']['S'])
                    if follower_exists:
                        user_name, photo, home = get_user_details(
                                                    follower['id1']['S'])
                        following_follower = check_if_user_following_user(
                                      data['user_id'], follower['id1']['S'])
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
            response['message'] = 'Request failed. Try again later.'

        return response, 200


class UserFollowingPostsFeeds(Resource):
    def post(self):
        """Returns users followings all posts"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id.')

        user_exists = check_if_user_exists(data['user_id'])

        if not user_exists:
            raise BadRequest('User does not exist.')

        feeds = []
        followings = [data['user_id']]

        users_followings = db.query(TableName='following_activity',
                                IndexName='id1-following',
                                KeyConditionExpression='id1 = :id and \
                                                        following = :f',
                                ExpressionAttributeValues={
                                    ':id': {'S': data['user_id']},
                                    ':f': {'S': 'True'}
                                }
                            )

        if users_followings.get('Items') != []:
            for item in users_followings['Items']:
                if item['type']['S'] == 'user':
                    followings.append(item['id2']['S'])

        if users_followings.get('LastEvaluatedKey') != None:
            followings_last_evaluated_key = True
            LastEvaluatedKey = users_followings['LastEvaluatedKey']
            while followings_last_evaluated_key:
                users_followings = db.query(TableName='following_activity',
                                IndexName='id1-following',
                                KeyConditionExpression='id1 = :id and \
                                                        following = :f',
                                ExpressionAttributeValues={
                                    ':id': {'S': data['user_id']},
                                    ':f': {'S': 'True'}
                                },
                                ExclusiveStartKey=LastEvaluatedKey
                            )

                if users_followings.get('Items') != []:
                    for item in users_followings['Items']:
                        if item['type']['S'] == 'user':
                            followings.append(item['id2']['S'])

                if users_followings.get('LastEvaluatedKey') == None:
                    followings_last_evaluated_key = False
                else:
                    LastEvaluatedKey = users_followings['LastEvaluatedKey']

        if data.get('last_evaluated_key') == None:
            following_feeds, last_evaluated_key = get_feeds(
                                            followings, 'posts')
        else:
            following_feeds, last_evaluated_key = get_feeds(followings, 
                                        'posts', data['last_evaluated_key'])

        if last_evaluated_key != None:
            response['last_evaluated_key'] = last_evaluated_key

        try:
            for post in following_feeds:
                user_name, profile_picture, home = get_user_details(
                                                post['email']['S'])
                if user_name == None:
                    del post
                else:
                    feed_id = post['email']['S'] + '_' + post['creation_time']['S']
                    liked = check_if_user_liked(feed_id, data['user_id'])
                    starred = check_if_user_starred(feed_id, data['user_id'])
                    commented = check_if_user_commented(feed_id, data['user_id'])
                    taking_off = check_if_taking_off(feed_id, 'posts')
                    added_to_fav = check_if_post_added_to_favorites(feed_id, 
                                                                  data['user_id'])
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
            response['message'] = 'Request failed!'

        return response, 200


class UserFollowingChallengesFeeds(Resource):
    def post(self):
        """Returns users followings challenges feed"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user\'s id.')

        user_exists = check_if_user_exists(data['user_id'])

        if not user_exists:
            raise BadRequest('User does not exist.')

        feeds = []

        followings = [data['user_id']]

        users_followings = db.query(TableName='following_activity',
                                IndexName='id1-following',
                                KeyConditionExpression='id1 = :id and \
                                                        following = :f',
                                ExpressionAttributeValues={
                                    ':id': {'S': data['user_id']},
                                    ':f': {'S': 'True'}
                                }
                            )

        if users_followings.get('Items') != []:
            for item in users_followings['Items']:
                if item['type']['S'] == 'user':
                    followings.append(item['id2']['S'])

        last_evaluated_key = False
        if users_followings.get('LastEvaluatedKey') != None:
            followings_last_evaluated_key = True
            LastEvaluatedKey = users_followings['LastEvaluatedKey']
            while last_evaluated_key:
                users_followings = db.query(TableName='following_activity',
                                IndexName='id1-following',
                                KeyConditionExpression='id1 = :id and \
                                                        following = :f',
                                ExpressionAttributeValues={
                                    ':id': {'S': data['user_id']},
                                    ':f': {'S': 'True'}
                                },
                                ExclusiveStartKey=LastEvaluatedKey
                            )
                if users_followings.get('LastEvaluatedKey') == None:
                    last_evaluated_key = False
                else:
                    LastEvaluatedKey = users_followings['LastEvaluatedKey']

        if data.get('last_evaluated_key') == None:
            following_feeds, last_evaluated_key = get_feeds(
                                            followings, 'challenges')
        else:
            following_feeds, last_evaluated_key = get_feeds(followings, 
                                    'challenges', data['last_evaluated_key'])

        if last_evaluated_key != None:
            response['last_evaluated_key'] = last_evaluated_key

        try:
            for challenge in following_feeds:
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
                    challenge['user'] = {}
                    challenge['user']['id'] = challenge['creator']
                    challenge['user']['name'] = {}
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

                    if challenge_accepted == True:
                        challenge['accepted_time'] = challenge['creation_time']

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

                feeds.append(challenge)

            response['message'] = 'Request successful.'
            response['results'] = feeds
        except:
            response['message'] = 'Request failed.'
        return response, 200


class FollowOthers(Resource):
    def get(self, user_email):
        response = {}

        greg_email = 'greg@givel.co'
        japan_email = 'parikh.japan30@gmail.com'

        try:
            greg = db.get_item(TableName='users', 
                            Key={'email': {'S': greg_email}})

            japan = db.get_item(TableName='users',
                            Key={'email': {'S': japan_email}})

            follow_others = []

            following_greg = check_if_user_following_user(user_email, 
                                                            greg_email)
            following_japan = check_if_user_following_user(user_email,
                                                            japan_email)

            g = {}
            g['user'] = {}
            g['user']['name'] = {}
            g['user']['id'] = greg['Item']['email']
            g['user']['name']['S'] = greg['Item']['first_name']['S'] + ' ' \
                                        +greg['Item']['last_name']['S']
            g['user']['following'] = {}
            g['user']['following']['BOOL'] = following_greg
            g['user']['home'] = greg['Item']['home']
            if greg['Item'].get('profile_picture') != None:
                g['user']['profile_picture'] = greg['Item']['profile_picture']

            j = {}
            j['user'] = {}
            j['user']['name'] = {}
            j['user']['id'] = japan['Item']['email']
            j['user']['name']['S'] = japan['Item']['first_name']['S'] + ' ' \
                                        +japan['Item']['last_name']['S']
            j['user']['following'] = {}
            j['user']['following']['BOOL'] = following_japan
            j['user']['home'] = japan['Item']['home']
            if japan['Item'].get('profile_picture') != None:
                j['user']['profile_picture'] = japan['Item']['profile_picture']

            follow_others.append(g)
            follow_others.append(j)

            response['message'] = 'Request Successful!'
            response['result'] = follow_others
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')



api.add_resource(UserFollowings, '/<user_email>/following')
api.add_resource(GetUsersFollowers, '/followers')
api.add_resource(GetUsersFollowings, '/following')
api.add_resource(UserFollowingPostsFeeds, '/following/posts')
api.add_resource(UserFollowingChallengesFeeds, '/following/challenges')
api.add_resource(FollowOthers, '/<user_email>/follow')

