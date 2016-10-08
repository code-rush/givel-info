import boto3

from app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_likes_table
from app.models import create_stars_table
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
        table_response = db.describe_table(TableName='stars')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('stars table exists!')
    except:
        stars = create_stars_table()
        print('stars table created!')
except:
    pass

# try:
#     try:
#         table_response = db.describe_table(TableName='comments')
#         if table_response['Table']['TableStatus'] == 'ACTIVE':
#             print('comments table created')
#     except:
#         comments = create_comments_table()
#         print('comments table created!')
# except:
#     pass


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
            feed_id = data['id']+'_'+data['key']
            if int(users_stars['Item']['givel_stars']['N']) < int(data['stars']):
                raise BadRequest('You don\'t have enough stars to donate.')
            if data.get('stars') != None:
                try:
                    get_star_post = db.get_item(TableName='stars',
                                          Key={'feed': {'S': feed_id},
                                               'user': {'S': user_email}
                                          }
                                      )
                    if get_star_post.get('Item') != None:
                        star_post = db.update_item(TableName='stars',
                                        Key={'feed': {'S': feed_id},
                                             'user': {'S': user_email}
                                        },
                                        UpdateExpression='SET stars = stars + :s',
                                        ExpressionAttributeValues={
                                            ':s': {'N': str(data['stars'])}
                                        }
                                    )
                    else:
                        star_post = db.put_item(TableName='stars',
                                        Item={'feed': {'S': feed_id},
                                              'user': {'S': user_email},
                                              'stars': {'N': str(data['stars'])}
                                        }
                                    )
                except:
                    raise BadRequest('Request Failed!')

                try:
                    user_stars = db.update_item(TableName='users',
                                Key={'email': {'S': user_email}},
                                UpdateExpression='SET givel_stars = givel_stars - :s',
                                ExpressionAttributeValues={
                                    ':s': {'N': str(data['stars'])}
                                }
                            )
                except:
                    rollback_post = db.delete_item(TableName='stars',
                                    Key={'feed': {'S': feed_id},
                                         'user': {'S': user_email}
                                    }
                                )
                    raise BadRequest('Request Failed! Try again later!')

                try:
                    post_owner = db.update_item(TableName='users',
                                    Key={'email': {'S': data['id']}},
                                    UpdateExpression='SET givel_stars = givel_stars + :s',
                                    ExpressionAttributeValues={
                                        ':s': {'N': str(data['stars'])}
                                    }
                                )
                except:
                    rollback_post = db.update_item(TableName='users',
                                    Key={'email': {'S': user_email}},
                                    UpdateExpression='SET givel_stars = givel_stars + :s',
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




api.add_resource(FeedLikes, '/likes/<user_email>/<feed>',
                            '/likes')
api.add_resource(FeedStars, '/stars/<user_email>/<feed>')




