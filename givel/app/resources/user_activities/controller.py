import boto3
import datetime

from app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_challenges_table
from app.models import create_posts_table
from app.helper import upload_file

user_activity_api_routes = Blueprint('activity_api', __name__)
api = Api(user_activity_api_routes)

BUCKET_NAME = 'posts'

db = boto3.client('dynamodb')
s3 = boto3.client('s3')

try: 
    table_response = db.describe_table(TableName='posts')
    if table_response['Table']['TableStatus'] == 'ACTIVE':
        print('Posts Table exists!')
    else:
        posts = create_posts_table()
        print('Posts Table created!')
except:
    pass

try:
    table_response = db.describe_table(TableName='challenges')
    if table_response['Table']['TableStatus']:
        print('Challenges Table exists!')
    else:
        challenges = create_challenges_table()
        print('Challenges Table created!')
except:
    pass


class UserFollowing(Resource):
    def get(self, user_email):
        """Returns list of users followings"""
        response = {}
        user = db.get_item(
                    TableName='users',
                    Key={'email': {'S': user_email}}
                )
        if user['Item'].get('following') != None:
            response['message'] = 'Success!'
            response['result'] = user['Item']['following']
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
                            }
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
                            }
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
        except:
            response['message'] = 'Failed to unfollow the user.'
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
            response['message'] = 'Success!'
            response['result'] = user['Item']['followers']
        else:
            response['message'] = 'Success!'
            response['message'] = 'You have no followers!'
        return response_message, 200


class UserPosts(Resource):
    def post(self, user_email):
        """Creates User Posts"""
        post_data = request.get_json(force=True)
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        post = db.put_item(TableName='posts',
                           Item={'user_email': {'S': user_email},
                                'date_time': {'S': date}
                           }
                      )
        try:
            if post_data['description']:
                post = db.update_item(TableName='posts',
                                      Key={'user_email': {'S': user_email},
                                           'date_time': {'S': date}
                                      },
                                      UpdateExpression='SET description = :d',
                                      ExpressionAttributeValues={
                                          ':d': {'S': post_data['description']}
                                      }
                                  )
        except:
            try:
                if post_data['picture']:
                    picture = request.files['picture_file']
                    picture_file = upload_file(picture, BUCKET_NAME, user_email)
                    post = db.update_item(TableName='posts',
                                          Key={'user_email': {'S': user_email},
                                               'date_time': {'S': date}
                                          },
                                          UpdateExpression='SET picture = :p',
                                          ExpressionAttributeValues={
                                              ':p': {'S': picture_file}
                                          }
                                      )
            except:
                pass

            try:
                if post_data['video']:
                    video = request.files['video_file']
                    video_file = upload_file(video, BUCKET_NAME, user_email)
                    post = db.update_item(TableName='posts',
                                          Key={'user_email': {'S': user_email},
                                               'date_time': {'S': date}
                                          },
                                          UpdateExpression='SET video = :v',
                                          ExpressionAttributeValues={
                                              ':v': {'S': video_file}
                                          }
                                      )
            except:
                pass
        return post, 200


# class ChallengePosts(Resource):
#     def post(self, user_email):
#         """Creates challenges"""
#         data = request.get_json(force=True)
#         date = datetime.datetime.strftime("%Y-%m-%d %H:%M:%S")
#         challenge_post = db.put_item(TableName='challenges',
#                                 Key={'user_email': {'S': user_email},
#                                      'date_time': {'S': date}
#                                 }
#                             )

#         try:
#             if data['description']:




api.add_resource(UserFollowing, '/<user_email>/following')
api.add_resource(UserFollowers, '/<user_email>/followers')
api.add_resource(UserPosts, '/<user_email>/post')


