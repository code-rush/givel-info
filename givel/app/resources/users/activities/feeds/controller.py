import boto3
import datetime

from app.app import app
from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_likes_table
from app.models import create_stars_activity_table
from app.models import create_comments_table

from app.helper import update_likes, update_value
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
            print('comments table created')
    except:
        comments = create_comments_table()
        print('comments table created!')
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
            feed_id = data['id']+'_'+data['key']
            if data['emotion'] != 'like' and data['emotion'] != 'unlike':
                raise BadRequest('emotion can only be either like or unlike')
            try:
                if data['emotion'] == 'like':
                    like_post = db.put_item(TableName='likes',
                                            Item={'feed': {'S': feed_id},
                                                  'user': {'S': user_email}
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

    # def post(self):
    #     response = {}
    #     data = request.get_json(force=True)

    #     if data.get('id') == None or data.get('key') == None:
    #         raise BadRequest('feed id and key not provided')
    #     else:
    #         try:
    #             people = db.query(TableName='likes',
    #                             IndexName='likes-feed-id-key',
    #                             Select='SPECIFIC_ATTRIBUTES',
    #                             ProjectionExpression='email'
    #                         )

    #             for p in people['Items']:
    #                 if 


class FeedStars(Resource):
    def put(self, user_email, feed):
        response = {}
        data = request.get_json(force=True)

        users_stars = db.get_item(TableName='users',
                        Key={'email': {'S': user_email}},
                        ConsistentRead=True,
                        ProjectionExpression='givel_stars')

        if str(feed) != 'posts' and str(feed) != 'challenges':
            raise BadRequest('Value of feed can only be either posts or challenges!')
        if int(users_stars['Item']['givel_stars']['N']) == 0:
            raise BadRequest('You have no stars left to donate.')
        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('feed id and key not provided')
        else:
            if int(data['stars']) == 0:
                raise BadRequest('Cannot donate less than 1 star.')
            if int(users_stars['Item']['givel_stars']['N']) < int(data['stars']):
                raise BadRequest('You don\'t have enough stars to donate.')

            feed_id = data['id']+'_'+data['key']
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

            if data.get('stars') != None:
                try:
                    star_post = db.put_item(TableName='stars_activity',
                                    Item={'email': {'S': user_email},
                                          'shared_time': {'S': date_time},
                                          'stars': {'N': str(data['stars'])},
                                          'shared_to': {'S': 'feed'},
                                          'shared_id': {'S': feed_id}
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
                    rollback_transaction = db.update_item(TableName='users',
                                    Key={'email': {'S': user_email}},
                                    UpdateExpression='SET givel_stars = givel_stars + :s, \
                                                      total_stars_shared = total_stars_shared - :s',
                                    ExpressionAttributeValues={
                                        ':s': {'N': str(data['stars'])}
                                    }
                                )
                    raise BadRequest('Request Failed! Try again later!')

                try:
                    post_owner = db.update_item(TableName='users',
                                    Key={'email': {'S': data['id']}},
                                    UpdateExpression='SET givel_stars = givel_stars + :s, \
                                                      total_stars_earned = total_stars_earned + :s',
                                    ExpressionAttributeValues={
                                        ':s': {'N': str(data['stars'])}
                                    }
                                )
                except:
                    rollback_post = db.update_item(TableName='users',
                                    Key={'email': {'S': user_email}},
                                    UpdateExpression='SET givel_stars = givel_stars + :s, \
                                                      total_stars_earned = total_stars_earned - :s',
                                    ExpressionAttributeValues={
                                        ':s': {'N': str(data['stars'])}
                                    }
                                )
                    raise BadRequest('Request Failed! Try again later!')

                update_stars_count = db.update_item(TableName=str(feed),
                                Key={'email': {'S': data['id']},
                                     'creation_time': {'S': data['key']}
                                },
                                UpdateExpression='SET stars = stars + :s',
                                ExpressionAttributeValues={
                                    ':s': {'N': str(data['stars'])}
                                }
                            )
                update_value(str(feed), data['id'], data['key'], 'stars', data['stars'])
                response['message'] = 'Successfully donated stars!'
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
            feed_id = data['id']+'_'+data['key']
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            add_comment = db.put_item(TableName='comments',
                            Item={'email': {'S': user_email},
                                  'creation_time': {'S': date_time},
                                  'feed_id': {'S': feed_id},
                                  'comment': {'S': data['comment']}
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
            feed_id = data['id']+'_'+data['key']

        # try:
            get_comments = db.query(TableName='comments',
                            IndexName='comments-feed-email',
                            Select='ALL_ATTRIBUTES',
                            KeyConditionExpression='feed_id = :e',
                            ExpressionAttributeValues={
                                ':e': {'S': feed_id}
                            }
                        )
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').rsplit(' ', 1)
            current_date = current_datetime[0].rsplit('-',2)
            current_time = current_datetime[1].rsplit(':',2)
            for comments in get_comments['Items']:
                comment_datetime = comments['creation_time']['S'].rsplit(' ',1)
                comment_date = comment_datetime[0].rsplit('-',2)
                comment_time = comment_datetime[1].rsplit(':',2)
                if comment_date[0] == current_date[0]:
                    if comment_date[1] == current_date[1]:
                        if comment_date[2] == current_date[2]:
                            if comment_time[0] == current_time[0]:
                                if comment_time[1] == current_time[1]:
                                    if comment_time[2] == current_time[2]:
                                        commented_time = '0s'
                                    else:
                                        commented_time = str(int(current_time[2]) - int(comment_time[2])) + 's'
                                else:
                                    commented_time = str(int(current_time[1]) - int(comment_time[1])) + 'm'
                            else:
                                commented_time = str(int(current_time[0]) - int(comment_time[0])) + 'hr'
                        else:
                            pt = int(current_date[2]) - int(comment_date[2])
                            if pt == 1:
                                commented_time = 'yesterday'
                            else:
                                commented_time = str(pt) + 'd'
                    else:
                        commented_time = str(int(current_date[1]) - int(comment_date[1])) + 'M'
                else:
                    commented_time = str(int(current_date[0]) - int(comment_date[0])) + 'yr'
                # comment_time = calculate_comment_deltatime(comments['date'])
                comments['commented_time'] = {}
                comments['commented_time']['S'] = commented_time
                comments['id'] = {}
                comments['id']['S'] = comments['email']['S']
                comments['key'] = {}
                comments['key']['S'] = comments['creation_time']['S']
                del comments['email']
                del comments['creation_time']

            response['message'] = 'Successfully fetched all comments'
            response['result'] = get_comments['Items']
            # except:
            #     response['message'] = 'Failed to fetch comments'
            return response, 200



api.add_resource(FeedLikes, '/likes/<user_email>/<feed>',
                            '/likes')
api.add_resource(FeedStars, '/stars/share/<user_email>/<feed>')
api.add_resource(FeedComments, '/comments/<user_email>')
api.add_resource(GetFeedComments, '/comments')




