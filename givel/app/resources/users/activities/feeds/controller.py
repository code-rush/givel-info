import boto3
import datetime

from app.app import app
from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_likes_table
from app.models import create_stars_activity_table
from app.models import create_comments_table
from app.models import create_shared_feeds_table

from app.helper import update_likes, update_value, update_stars_count
from app.helper import get_user_details, STATES

from app.helper import mid_west_states, southeast_states, northeast_states
from app.helper import pacific_states, southwest_states, rocky_mountain_states

from werkzeug.exceptions import BadRequest

feed_activity_api_routes = Blueprint('feed_activity_api', __name__)
api = Api(feed_activity_api_routes)


db = boto3.client('dynamodb')

try: 
    try:
        table_response = db.describe_table(TableName='likes')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('likes table exists!')
    except:
        likes = create_likes_table()
        print('likes table created!')
except:
    pass

try: 
    try:
        table_response = db.describe_table(TableName='stars_activity')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('stars table exists!')
    except:
        stars = create_stars_activity_table()
        print('stars table created!')
except:
    pass

try:
    try:
        table_response = db.describe_table(TableName='comments')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('comments table exists')
    except:
        comments = create_comments_table()
        print('comments table created!')
except:
    pass

try:
    try:
        table_response = db.describe_table(TableName='shared_feeds')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('shared_feeds table exists')
    except:
        shared_feeds = create_shared_feeds_table()
        print('shared_feeds table created!')
except:
    pass


class FeedLikes(Resource):
    def put(self, user_email, feed):
        response = {}
        data = request.get_json(force=True)

        if str(feed) != 'posts' and str(feed) != 'challenges':
            raise BadRequest('Value of feed can only be either posts or challenges!')
        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('feed id and key not provided')
        else:
            feed_id = None
            if str(data['id']) == 'organization':
                feed_id = str(data['key'])
            else:
                feed_id = data['id']+'_'+data['key']

            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if data['emotion'] != 'like' and data['emotion'] != 'unlike':
                raise BadRequest('emotion can only be either like or unlike')
            try:
                if data['emotion'] == 'like':
                    like_post = db.put_item(TableName='likes',
                                            Item={'feed': {'S': feed_id},
                                                  'user': {'S': user_email}
                                            }
                                        )
                    if data['id'] != 'organization':
                        notification = db.put_item(TableName='notifications',
                                Item={'notify_to': {'S': data['id']},
                                      'creation_time': {'S': date_time},
                                      'email': {'S': user_email},
                                      'from': {'S': 'feed'},
                                      'feed_id': {'S': feed_id},
                                      'checked': {'BOOL': False},
                                      'notify_for': {'S': 'like'},
                                      'feed_type': {'S': str(feed)}
                                }
                            )
                    response['message'] = 'Success! Feed liked!'
                elif data.get('emotion') == 'unlike':
                    unlike_post = db.delete_item(TableName='likes',
                                            Key={'feed': {'S': feed_id},
                                                 'user': {'S': user_email}
                                            }
                                        )
                    response['message'] = 'Success! Feed unliked!'
                update_likes(str(feed), data['id'], data['key'], data['emotion'])
                update_value(str(feed), data['id'], data['key'], data['emotion'])
                return response, 200
            except:
                raise BadRequest('Request Failed!')


class GetFeedLikes(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('feed id and key not provided')
        else:
            feed_id = None
            if str(data['id']) == 'organization':
                feed_id = str(data['key'])
            else:
                feed_id = data['id']+'_'+data['key']

            try:
                likes = db.query(TableName='likes',
                                Select='ALL_ATTRIBUTES',
                                KeyConditionExpression='feed = :feed',
                                ExpressionAttributeValues={
                                    ':feed': {'S': feed_id}
                                }
                            )

                for like in likes['Items']:
                    email = like['user']['S']
                    user_name, profile_picture, home = get_user_details(email)
                    if user_name == None:
                        del like
                    else:
                        like['user'] = {}
                        like['user']['name'] = {}
                        like['user']['home'] = {}
                        like['user']['profile_picture'] = {}
                        like['user']['name']['S'] = user_name
                        like['user']['profile_picture']['S'] = profile_picture
                        like['user']['home']['S'] = home
                        like['user']['id'] = {}
                        like['user']['id']['S'] = email

                response['message'] = 'Successfully fetched all likes'
                response['result'] = likes['Items']
            except:
                response['message'] = 'Failed to fetch likes'
            return response, 200


class FeedStars(Resource):
    def put(self, user_email, feed):
        response = {}
        data = request.get_json(force=True)

        user = db.get_item(TableName='users',
                        Key={'email': {'S': user_email}},
                        ConsistentRead=True
                    )

        if str(feed) != 'posts' and str(feed) != 'challenges':
            raise BadRequest('Value of feed can only be either posts or challenges!')
        if int(user['Item']['givel_stars']['N']) == 0:
            raise BadRequest('You have no stars left to donate.')
        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('feed id and key not provided')
        if data.get('id') == user_email:
            raise BadRequest('You cannot give stars to your own post!')
        else:
            if int(data['stars']) == 0:
                raise BadRequest('Cannot donate less than 1 star.')
            if int(user['Item']['givel_stars']['N']) < int(data['stars']):
                raise BadRequest('You don\'t have enough stars to donate.')

            feed_id = None
            region = None
            st = user['Item']['home']['S'].rsplit(' ', 1)[1]

            if data['id'] == 'organization':
                feed_id = str(data['key'])
                if STATES[st] in pacific_states:
                    region = 'pacific_region_feed_stars'
                elif STATES[st] in southwest_states:
                    region = 'south_west_region_feed_stars'
                elif STATES[st] in mid_west_states:
                    region = 'mid_west_region_feed_stars'
                elif STATES[st] in rocky_mountain_states:
                    region = 'rocky_mountain_region_feed_stars'
                elif STATES[st] in southeast_states:
                    region = 'south_east_region_feed_stars'
                elif STATES[st] in northeast_states:
                    region = 'north_east_region_feed_stars'
            else:
                feed_id = data['id']+'_'+data['key']


            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

            if data.get('stars') != None:
                try:
                    if str(data['id']) == 'organization':
                        star_post = db.put_item(TableName='stars_activity',
                                        Item={'email': {'S': user_email},
                                              'shared_time': {'S': date_time},
                                              'stars': {'N': str(data['stars'])},
                                              'shared_to': {'S': 'organizations_feed'},
                                              'shared_id': {'S': feed_id}
                                        }
                                    )
                    else:
                        star_post = db.put_item(TableName='stars_activity',
                                        Item={'email': {'S': user_email},
                                              'shared_time': {'S': date_time},
                                              'stars': {'N': str(data['stars'])},
                                              'shared_to': {'S': 'feed'},
                                              'shared_id': {'S': feed_id}
                                        }
                                    )

                        notifications = db.put_item(TableName='notifications',
                                        Item={'notify_to': {'S': data['id']},
                                              'creation_time': {'S': date_time},
                                              'email': {'S': user_email},
                                              'from': {'S': 'feed'},
                                              'feed_id': {'S': feed_id},
                                              'checked': {'BOOL': False},
                                              'notify_for': {'S': 'stars'},
                                              'feed_type': {'S': str(feed)},
                                              'stars': {'N': str(data['stars'])}
                                        }
                                    )
                except:
                    raise BadRequest('Request Failed!')

                try:
                    user_stars = db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='SET givel_stars = givel_stars - :s, \
                                                  total_stars_shared = total_stars_shared + :s',
                                ExpressionAttributeValues={
                                    ':s': {'N': str(data['stars'])}
                                }
                            )
                except:
                    rollback_post = db.delete_item(TableName='stars_activity',
                                    Key={'email': {'S': user_email},
                                         'shared_time': {'S': date_time}
                                    }
                                )
                    rollback_notifcation = db.delete_item(TableName='notifications',
                                    Key={'notify_to': {'S': data['id']},
                                         'creation_time': {'S': date_time}
                                    }
                                )
                    raise BadRequest('Request Failed! Try again later!')

                try:
                    if str(data['id']) == 'organization':
                        org = db.update_item(TableName='organizations',
                                    Key={'name': {'S': str(data['key'])}},
                                    UpdateExpression='SET feed_stars = feed_stars + :s, \
                                                      SET #rs = #rs + :s',
                                    ExpressionAttributeNames={
                                        '#rs': region
                                    },
                                    ExpressionAttributeValues={
                                        ':s': {'N': str(data['stars'])}
                                    }
                                )
                    else:
                        post_owner = db.update_item(TableName='users',
                                    Key={'email': {'S': data['id']}},
                                    UpdateExpression='SET givel_stars = givel_stars + :s, \
                                                      total_stars_earned = total_stars_earned + :s',
                                    ExpressionAttributeValues={
                                        ':s': {'N': str(data['stars'])}
                                    }
                                )
                except:
                    rollback_post = db.delete_item(TableName='stars_activity',
                                    Key={'email': {'S': user_email},
                                         'shared_time': {'S': date_time}
                                    }
                                )
                    rollback_transaction = db.update_item(TableName='users',
                                    Key={'email': {'S': user_email}},
                                    UpdateExpression='SET givel_stars = givel_stars + :s, \
                                                      total_stars_shared = total_stars_shared - :s',
                                    ExpressionAttributeValues={
                                        ':s': {'N': str(data['stars'])}
                                    }
                                )
                    rollback_notifcation = db.delete_item(TableName='notifications',
                                    Key={'notify_to': {'S': data['id']},
                                         'creation_time': {'S': date_time}
                                    }
                                )
                    raise BadRequest('Request Failed! Try again later!')

                update_stars_count(str(feed), str(data['id']), str(data['key']), str(data['stars']))
                update_value(str(feed), data['id'], data['key'], 'stars', str(data['stars']))
                response['message'] = 'Successfully donated stars!'
            return response, 200


class GetFeedStars(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('feed id and key not provided')
        else:
            feed_id = None
            shared_to = None
            if str(data['id']) == 'organization':
                feed_id = str(data['key'])
                shared_to = 'organization'
            else:
                feed_id = data['id']+'_'+data['key']
                shared_to = 'feed'

            try:
                stars = db.query(TableName='stars_activity',
                            IndexName='shared-to-id',
                            Select='SPECIFIC_ATTRIBUTES',
                            KeyConditionExpression='shared_to = :to \
                                                 AND shared_id = :id',
                            ProjectionExpression='email, stars',
                            ExpressionAttributeValues={
                                ':to': {'S': shared_to},
                                ':id': {'S': feed_id}
                            }
                        )

                for star in stars['Items']:
                    user_name, profile_picture, home = get_user_details(star['email']['S'])
                    if user_name == None:
                        del star
                    else:
                        star['user'] = {}
                        star['user']['name'] = {}
                        star['user']['profile_picture'] = {}
                        star['user']['name']['S'] = user_name
                        star['user']['profile_picture']['S'] = profile_picture
                        star['user']['id'] = star['email']
                        del star['email']

                response['message'] = 'Successfully fetched all stars'
                response['result'] = stars['Items']
            except:
                response['message'] = 'Failed to fetch stars'
            return response, 200


class FeedComments(Resource):
    def post(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('feed id and key not provided')
        if data.get('comment') == None:
            raise BadRequest('Cannot create an empty comment!')
        else:
            feed_id = None
            if data['id'] == 'organization':
                feed_id = data['key']
            else:
                feed_id = data['id']+'_'+data['key']

            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if data.get('tags') != None:
                add_comment = db.put_item(TableName='comments',
                            Item={'email': {'S': user_email},
                                  'creation_time': {'S': date_time},
                                  'feed_id': {'S': feed_id},
                                  'comment': {'S': data['comment']},
                                  'tagged': {'SS': data['tags']}
                            }
                        )
                for i in range(0, len(data['tags'])):
                    tag_notification = db.put_item(TableName='notifications',
                            Item={'notify_to': {'S': data['tags'][i]['user_id']},
                                  'creation_time': {'S': date_time},
                                  'email': {'S': user_email},
                                  'from': {'S': 'feed'},
                                  'feed_id': {'S': feed_id},
                                  'checked': {'BOOL': False},
                                  'notify_for': {'S': 'tagging'},
                                  'tagged_where': {'S': 'comment'},
                                  'comment_id': 
                                      {'S': user_email + '_' + date_time} 
                            }
                        )
            else:
                add_comment = db.put_item(TableName='comments',
                            Item={'email': {'S': user_email},
                                  'creation_time': {'S': date_time},
                                  'feed_id': {'S': feed_id},
                                  'comment': {'S': data['comment']}
                            }
                        )

            if data['id'] != 'organization':
                notification = db.put_item(TableName='notifications',
                            Item={'notify_to': {'S': data['id']},
                                  'creation_time': {'S': date_time},
                                  'email': {'S': user_email},
                                  'from': {'S': 'feed'},
                                  'feed_id': {'S': feed_id},
                                  'checked': {'BOOL': False},
                                  'notify_for': {'S': 'comment'},
                                  'comment_id': 
                                      {'S': user_email + '_' + date_time}
                            }
                        )

            response['message'] = 'Comment successfully created!'
            return response, 200

    def delete(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('Comment ID and Key not provided.')
        if data['id'] != str(user_email):
            raise BadRequest('Only the creator can delete the comment')
        else:
            delete_comment = db.delete_item(TableName='comments',
                            Key={'email': {'S': data['id']},
                                 'creation_time': {'S': data['key']}
                            }
                        )
            response['message'] = 'Comment deleted!'
            return response, 200

    def put(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('Comment ID and Key not provided.')
        if data['id'] != str(user_email):
            raise BadRequest('Only the creator can edit the comment')
        else:
            edit_comment = db.update_item(TableName='comments',
                            Key={'email': {'S': data['id']},
                                 'creation_time': {'S': data['key']}
                            },
                            UpdateExpression='SET #com = :com',
                            ExpressionAttributeNames={
                                '#com': 'comment'
                            },
                            ExpressionAttributeValues={
                                ':com': {'S': data['comment']}
                            }
                        )
            response['message'] = 'Comment edited!'
            return response, 200


class GetFeedComments(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('feed id and key not provided')
        else:
            feed_id = None
            if str(data['id']) == 'organization':
                feed_id = str(data['key'])
            else:
                feed_id = data['id']+'_'+data['key']

            try:
                get_comments = db.query(TableName='comments',
                                IndexName='comments-feed-email',
                                Select='ALL_ATTRIBUTES',
                                KeyConditionExpression='feed_id = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': feed_id}
                                }
                            )
                for comment in get_comments['Items']:
                    user_name, profile_picture, home = get_user_details(comment['email']['S'])
                    if user_name == None:
                        del comment
                    else:
                        comment['id'] = {}
                        comment['id']['S'] = comment['email']['S']
                        comment['key'] = {}
                        comment['key']['S'] = comment['creation_time']['S']
                        comment['user'] = {}
                        comment['user']['name'] = {}
                        comment['user']['profile_picture'] = {}
                        comment['user']['name']['S'] = user_name
                        comment['user']['profile_picture']['S'] = profile_picture
                        comment['user']['id'] = comment['email'] 
                        del comment['email']

                response['message'] = 'Successfully fetched all comments'
                response['result'] = get_comments['Items']
            except:
                response['message'] = 'Failed to fetch comments'
            return response, 200


class ShareFeeds(Resource):
    """Share feeds with a user on Givel"""
    def put(self, user_email, feed):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None and data.get('key') == None:
            raise BadRequest('Please provide ID and KEY to share the feed')
        if data.get('shared_to') == None:
            raise BadRequest('Please provide the user with whom you are \
                             sharing the feed with')
        if str(feed) != 'post' and str(feed) != 'challenge':
            raise BadRequest('feed can be either challenge or post')
        else:
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            feed_id = data['id']+'_'+data['key']

            try:
                share_feed = db.put_item(TableName='shared_feeds',
                                        Item={'email': {'S': user_email},
                                              'creation_time': {'S': date_time},
                                              'feed_type': {'S': str(feed)},
                                              'shared_to': {'S': data['shared_to']},
                                              'feed_id': {'S': feed_id}
                                             }
                                      )

                if data['id'] != 'organization':
                    notification = db.put_item(TableName='notifications',
                                    Item={'notify_to': {'S': data['id']},
                                          'creation_time': {'S': date_time},
                                          'email': {'S': user_email},
                                          'from': {'S': 'feed'},
                                          'notify_for': {'S': 'share'},
                                          'feed_id': {'S': feed_id},
                                          'checked': {'BOOL': False},
                                          'feed_type': {'S': str(feed)+'s'}
                                    }
                                )

                response['message'] = 'Post successfully shared!'
            except:
                response['message'] = 'Request failed! Try again later'

            return response, 200



api.add_resource(FeedLikes, '/likes/<user_email>/<feed>')
api.add_resource(GetFeedLikes,'/likes')
api.add_resource(FeedStars, '/stars/share/<user_email>/<feed>')
api.add_resource(GetFeedStars, '/stars')
api.add_resource(FeedComments, '/comments/<user_email>')
api.add_resource(GetFeedComments, '/comments')
api.add_resource(ShareFeeds, '/share/<feed>/<user_email>')

