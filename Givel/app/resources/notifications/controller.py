import boto3

from app.app import app

from flask import Blueprint, request, json
from flask_restful import Resource, Api

from app.models import create_notifications_table

from app.helper import check_if_user_exists, get_user_details
from app.helper import check_if_user_liked, check_if_user_starred
from app.helper import check_if_user_commented, check_if_taking_off

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
    def get(self, user_email):
        response = {}

        users_notifications = []
        user_exsits = check_if_user_exists(user_email)
        if user_exsits:
            notifications = db.query(TableName='notifications',
                            Select='ALL_ATTRIBUTES',
                            KeyConditionExpression='notify_to = :e',
                            ExpressionAttributeValues={
                                ':e': {'S': user_email}
                            }
                        )
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
                    # notification['notification']['S'] = '{} '.format(
                    #                user_name) + 'started following you'

                elif notification['from']['S'] == 'follower' \
                  and notification['notify_for']['S'] == 'stars':
                    notification['from']['S'] = user_name
                    notification['activity'] = notification['notify_for']
                    # notification['notification']['S'] = '{} '.format(
                    #        user_name) + 'gave you {} stars '.format(
                    #        notification['stars']['N']) + 'for being awesome'

                elif notification['from']['S'] == 'feed':
                    notification['feed'] = {}
                    notification['feed']['id'] = notification['feed_id']
                    notification['feed']['type'] = notification['feed_type']
                    content_name_holder = None
                    if notification['feed_type']['S'] == 'posts':
                        content_name_holder = 'content'
                    elif notification['feed_type']['S'] == 'challenges':
                        content_name_holder = 'description'
                    f_id = notification['feed_id']['S'].rsplit('_', 1)[0]
                    f_key = notification['feed_id']['S'].rsplit('_', 1)[1]
                    feed = db.get_item(
                            TableName=notification['feed_type']['S'],
                            Key={'email': {'S': f_id},
                                 'creation_time': {'S': f_key}
                            }
                        )

                    # notification['from']['S'] = user_name
                    notification['where'] = notification['feed_type']['S'][:-1]
                    notification['activity'] = notification['notify_for']
                    notification['feed']['content'] = feed['Item'][content_name_holder]
                    # if notification['notify_for']['S'] == 'stars':
                        
                    #     # notification['notification']['S'] = '{} '.format(
                    #     #   user_name) + 'gave you {} stars '.format(
                    #     #   notification['stars']['N']) + 'for the {} {}'.format(
                    #     #               notification['feed_type']['S'][:-1], 
                    #     #               feed['Item'][content_name_holder]['S'])
                    
                    # elif notification['notify_for']['S'] == 'like':
                    #     notification['notification']['S'] = '{} '.format(
                    #             user_name) + 'liked your {} {}'.format( 
                    #               notification['feed_type']['S'][:-1],
                    #               feed['Item'][content_name_holder]['S'])
                    
                    # elif notification['notify_for']['S'] == 'share':
                    #     notification['notification']['S'] = '{} '.format(
                    #             user_name) + 'shared your {} {}'.format( 
                    #               notification['feed_type']['S'][:-1],
                    #               feed['Item'][content_name_holder]['S'])
                    
                    # elif notification['notify_for']['S'] == 'comment':
                    #     notification['comment_id'] = notification['comment_id']
                    #     notification['notification']['S'] = '{} '.format(
                    #             user_name) + 'commented on your {} {}'.format(
                    #                 notification['feed_type']['S'][:-1].
                    #                 feed['Item'][content_name_holder]['S'])
                    
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
                            notification['id'] = notification['comment_id']
                            notification['content'] = comment['Item']['comment']
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
                del notification['feed_id']
                del notification['feed_type']
                users_notifications.append(notification)
            response['message'] = 'Successfully fetched all notifications.'
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
            user_name = None
            profile_picture = None
            home_community = None
            user_id = None
            if data['feed_type'] == 'challenges':
                user_id = feed['Item']['creator']['S']
                user_name, profile_picture, home_community = get_user_details(
                                                                      user_id)
            else:
                user_id = user_email
                user_name, profile_picture, home_community = get_user_details(
                                                                      user_id)
            liked = check_if_user_liked(data['feed_id'], user_email)
            starred = check_if_user_starred(data['feed_id'], user_email)
            commented = check_if_user_commented(data['feed_id'], user_email)
            taking_off = check_if_taking_off(data['feed_id'], data['feed_type'])
            feed['user'] = {}
            feed['user']['id'] = {}
            feed['user']['name'] = {}
            feed['user']['profile_picture'] = {}
            feed['user']['id']['S'] = user_id
            feed['user']['name']['S'] = user_name
            feed['user']['profile_picture']['S'] = profile_picture
            feed['feed'] = {}
            feed['feed']['id'] = feed['Item']['email']
            feed['feed']['key'] = feed['Item']['creation_time']
            feed['liked'] = {}
            feed['starred'] = {}
            feed['commented'] = {}
            feed['taking_off'] = {}
            feed['taking_off']['BOOL'] = taking_off
            feed['liked']['BOOL'] = liked
            feed['starred']['BOOL'] = starred
            feed['commented']['BOOL'] = commented
            del feed['Item']['email']
            del feed['Item']['value']
            del feed['Item']['only_to_followers']
            del feed['ResponseMetadata']

            response['message'] = 'Successfully fetched the notification!'
            response['result'] = feed
        return response, 200


api.add_resource(GetUserNotifications, '/<user_email>')
api.add_resource(GetNotification, '/<user_email>')

