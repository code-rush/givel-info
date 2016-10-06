import boto3

from app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_likes_table
from app.helper import update_likes
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


class FeedLikes(Resource):
    def put(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('feed id and key not provided')
        else:
            if data['emotion'] != 'like' or data['emotion'] !='dislike':
                raise BadRequest('emotion can only be either like or dislike')
            try:
                if data['emotion'] == 'like':
                    like_post = db.put_item(TableName='likes',
                                            Item={'email': {'S': user_email},
                                                 'feed_id': {'S': data['id']},
                                                 'feed_key': {'S': data['key']}
                                            }
                                        )
                    response['message'] = 'Success! Feed liked!'
                elif data.get('emotion') == 'dislike':
                    dislike_post = db.delete_item(TableName='likes',
                                            Key={'email': {'S': user_email}})
                    response['message'] = 'Success! Feed disliked!'
                update_likes(data['id'], data['key'], data['emotion'])
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


api.add_resource(FeedLikes, '/likes/<user_email>',
                            '/likes')




