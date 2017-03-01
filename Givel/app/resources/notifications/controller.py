import boto3

from app.app import app

from flask import Blueprint, request, json
from flask_restful import Resource, Api

from app.models import create_notifications_table

from app.helper import (check_if_user_exists, get_user_details,
                        check_if_user_liked, check_if_user_starred,
                        check_if_user_commented, check_if_taking_off,
                        check_if_post_added_to_favorites,
                        get_challenge_accepted_users, 
                        check_if_challenge_accepted,
                        check_if_user_following_user,
                        update_notifications_activity_page)

from werkzeug.exceptions import BadRequest


notifications_api_routes = Blueprint('notification_api', __name__)
api = Api(notifications_api_routes)


db = boto3.client('dynamodb')

try:
    try:
        table_response = db.describe_table(TableName='notifications')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('notifications Table exists!')
    except:
        notifications = create_notifications_table()
        print('notifications Table created!')
except:
    pass


class GetUserNotifications(Resource):
    """Returns user's all notifications"""
    def post(self):
        response = {}

        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user_id' \
                         + ' to get their notifications.')
        else:
            user_email = data['user_id']
            user_exsits = check_if_user_exists(user_email)
        
        users_notifications = []
        
        if user_exsits:
            if data.get('last_evaluated_key') != None:
                notifications = db.query(TableName='notifications',
                                    Select='ALL_ATTRIBUTES',
                                    Limit=20,
                                    KeyConditionExpression='notify_to = :e',
                                    ExpressionAttributeValues={
                                        ':e': {'S': user_email}
                                    },
                                    ExclusiveStartKey=data['last_evaluated_key'],
                                    ScanIndexForward=False
                                )
            else:
                notifications = db.query(TableName='notifications',
                                Select='ALL_ATTRIBUTES',
                                Limit=20,
                                KeyConditionExpression='notify_to = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': user_email}
                                },
                                ScanIndexForward=False
                            )

            if notifications.get('LastEvaluatedKey') != None:
                response['last_evaluated_key'] = notifications['LastEvaluatedKey']

            for notification in notifications['Items']:
                user_name, profile_picture, home = get_user_details(
                                               notification['email']['S'])
                notification['user']= {}
                notification['user']['profile_picture'] = {}
                notification['user']['profile_picture']['S'] = profile_picture
                notification['user']['name'] = {}
                notification['user']['name']['S'] = user_name
                notification['user']['id'] = notification['email']
                notification['notification'] = {}
                notification['notification']['id'] = notification['notify_to']
                notification['notification']['key'] = notification['creation_time']

                if notification['from']['S'] == 'user' \
                  and notification['notify_for']['S'] == 'following':
                    notification['from']['S'] = user_name
                    notification['activity'] = notification['notify_for']
                    
                elif notification['from']['S'] == 'follower' \
                  and notification['notify_for']['S'] == 'stars':
                    notification['from']['S'] = user_name
                    notification['activity'] = notification['notify_for']

                elif notification['from']['S'] == 'feed':
                    notification['feed'] = {}
                    notification['feed']['id'] = notification['feed_id']
                    content_name_holder = None
                    f_id = notification['feed_id']['S'].rsplit('_', 1)[0]
                    f_key = notification['feed_id']['S'].rsplit('_', 1)[1]
                    del notification['feed_id']
                    if notification.get('feed_type') != None:
                        notification['feed']['type'] = notification['feed_type']
                        if notification['feed_type']['S'] == 'posts':
                            content_name_holder = 'content'
                        elif notification['feed_type']['S'] == 'challenges':
                            content_name_holder = 'description'

                        feed = db.get_item(
                                TableName=notification['feed_type']['S'],
                                Key={'email': {'S': f_id},
                                     'creation_time': {'S': f_key}
                                }
                            )

                        notification['where'] = notification['feed_type']['S'][:-1]
                        if feed.get('Item') == None:
                            notification['feed']['content'] = {}
                            notification['feed']['content']['S'] = ''
                        else:
                            notification['feed']['content'] = feed['Item']\
                                                      [content_name_holder]
                        del notification['feed_type']

                    notification['activity'] = notification['notify_for']
                  
                    if notification['notify_for']['S'] == 'comment':
                        notification['feed']['type'] = {}
                        f1 = db.get_item(TableName='posts',
                                Key={'email': {'S': f_id},
                                     'creation_time': {'S': f_key}})

                        f2 = db.get_item(TableName='challenges',
                                Key={'email': {'S': f_id},
                                     'creation_time': {'S': f_key}})

                        if f1.get('Item') == None and f2.get('Item') == None:
                            notification['feed']['content'] = {}
                            notification['feed']['content']['S'] = ''
                        elif f1.get('Item') == None:
                            notification['feed']['type']['S'] = 'challenges'
                            notification['feed']['content'] = f2['Item']['description']
                        else:
                            notification['feed']['type']['S'] = 'posts'
                            notification['feed']['content'] = f1['Item']['content']
                    
                    if notification['notify_for']['S'] == 'tagging':
                        if notification['tagged_where']['S'] == 'comment':
                            c_id = notification['comment_id']['S'].rsplit('_', 1)[0]
                            c_key = notification['comment_id']['S'].rsplit('_', 1)[1]
                            comment = db.get_item(TableName='comments',
                                Key={'email': {'S': c_id},
                                     'creation_time': {'S': 'c_key'}
                                }
                            )
                            notification['comment'] =  {}
                            notification['comment']['id'] = notification['comment_id']
                            if comment.get('Item') == None:
                                notification['comment']['content'] = {}
                                notification['comment']['content']['S'] = ''
                            else:
                                notification['comment']['content'] = comment['Item']['comment']
                            # notification['notification']['S'] = '{} '.format(
                            #      user_name) + 'tagged you in a comment {}'.format(
                            #                       comment['Item']['comment']['S'])
                        
                        elif notification['tagged_where']['S'] == 'post':
                            notification['notification']['S'] = '{} '.format(
                                  user_name) + 'tagged you in a post {}'.format( 
                                         feed['Item'][content_name_holder]['S'])

                del notification['email']
                del notification['from']
                del notification['notify_for']
                del notification['notify_to']
                users_notifications.append(notification)
            response['message'] = 'Request successful.'
            response['result'] = users_notifications
        else:
            response['message'] = 'Request failed! User does not exist.'

        return response, 200

    def put(self, user_email):
        """Changes the state to seen once notification is checked"""
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None and data.get('key') == None:
            raise BadRequest('Please provide notification id and key.')

        try:
            if data.get('checked') != None:
                checked = False
                if data['checked'] == True:
                    checked = True
                notification = db.update_item(TableName='notifications',
                                    Key={'notify_to': {'S': data['id']},
                                         'creation_time': {'S': data['key']}
                                    },
                                    UpdateExpression='SET checked = :c',
                                    ExpressionAttributeValues={
                                        ':c': {'BOOL': checked}
                                    }
                                )
                response['message'] = 'Request successful!'
        except:
            response['message'] = 'Request Failed!'

        return response, 200



class GetNotification(Resource):
    def post(self, user_email):
        """Returns the notification activity"""    
        response = {}
        data = request.get_json(force=True)

        if data.get('feed_id') == None:
            raise BadRequest('Please provide feed_id')

        if data.get('feed_id') != None:
            if data.get('feed_type') == None:
                raise BadRequest('Please provide feed_type')

            f_id = data['feed_id'].rsplit('_', 1)[0]
            f_key = data['feed_id'].rsplit('_', 1)[1]
            feed = db.get_item(TableName=data['feed_type'],
                        Key={'email': {'S': f_id},
                             'creation_time': {'S': f_key}
                        }
                    )
            if feed.get('Item') == None:
                response['message'] = 'Request successful!'
                response['result'] = 'This feed no longer exists!'
            else:
                user_name = None
                profile_picture = None
                home_community = None
                user_id = None
                added_to_fav = None
                accepted_users = None
                challenge_accepted = None
                following = None
                if data['feed_type'] == 'challenges':
                    user_id = feed['Item']['creator']['S']
                    user_name, profile_picture, home_community = get_user_details(
                                                                          user_id)
                    accepted_users_list = get_challenge_accepted_users(
                                              data['feed_id'], user_email)
                    challenge_accepted, state = check_if_challenge_accepted(data['feed_id'],
                                                                      user_email)
                    following = check_if_user_following_user(user_email, 
                                                              user_id)
                else:
                    user_id = feed['Item']['email']['S']
                    user_name, profile_picture, home_community = get_user_details(
                                                                          user_id)
                    added_to_fav = check_if_post_added_to_favorites(data['feed_id'], 
                                                                  user_email)
                    following = check_if_user_following_user(user_email, 
                                                              user_id)
                liked = check_if_user_liked(data['feed_id'], user_email)
                starred = check_if_user_starred(data['feed_id'], user_email)
                commented = check_if_user_commented(data['feed_id'], user_email)
                taking_off = check_if_taking_off(data['feed_id'], data['feed_type'])
                f = feed['Item']
                f['user'] = {}
                f['user']['id'] = {}
                f['user']['name'] = {}
                f['user']['profile_picture'] = {}
                f['user']['id']['S'] = user_id
                f['user']['name']['S'] = user_name
                f['user']['profile_picture']['S'] = profile_picture
                f['feed'] = {}
                if data['feed_type'] == 'challenges':
                    f['feed']['id'] = feed['Item']['creator']
                    f['feed']['key'] = feed['Item']['creation_key']
                elif data['feed_type'] == 'posts':
                    f['feed']['id'] = feed['Item']['email']
                    f['feed']['key'] = feed['Item']['creation_time']
                f['liked'] = {}
                f['starred'] = {}
                f['commented'] = {}
                f['taking_off'] = {}
                f['taking_off']['BOOL'] = taking_off
                f['liked']['BOOL'] = liked
                f['starred']['BOOL'] = starred
                f['commented']['BOOL'] = commented

                if data['feed_type'] == 'posts':
                    f['added_to_fav'] = {}
                    f['added_to_fav']['BOOL'] = added_to_fav
                    if feed['Item']['email']['S'] != user_email:
                        f['user']['following'] = {}
                        f['user']['following']['BOOL'] = following
                elif data['feed_type'] == 'challenges':
                    if state != None:
                        f['state'] = {}
                        f['state']['S'] = state
                    f['accepted'] = {}
                    f['accepted']['BOOL'] = challenge_accepted
                    f['accepted_users'] = {}
                    f['accepted_users']['SS'] = accepted_users_list 
                    if feed['Item']['creator']['S'] != user_email:
                        f['user']['following'] = {}
                        f['user']['following']['BOOL'] = following

                del feed['Item']['email']
                del feed['Item']['value']
                del feed['Item']['only_to_followers']
                del feed['ResponseMetadata']

                response['message'] = 'Successfully fetched the notification!'
                response['result'] = f
        return response, 200


class NotificationActivityPage(Resource):
    def get(self, user_email):
        response = {}

        data = db.get_item(TableName='notifications_activity_page',
                            Key={'email': {'S': user_email}})

        if data.get('Item') != None:
            response['seen'] = data['Item']['seen']
        else:
            response['seen'] = {}
            response['seen']['BOOL'] = True

        response['message'] = 'Request successful.'
        return response, 200

    def put(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('seen') == None:
            raise BadRequest('Please provide "seen" parameter with boolean '\
                             + 'value(true) if user has seen the page.')
        else:
            update_notifications_activity_page(user_email, data['seen'])

            response['message'] = 'Request successful.'
        return response, 200



api.add_resource(GetUserNotifications, '/')
api.add_resource(GetNotification, '/<user_email>')
api.add_resource(NotificationActivityPage, '/activity/page/<user_email>')

