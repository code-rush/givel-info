import boto3
import datetime

from app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_challenges_table
from app.models import create_posts_table
from app.helper import upload_file

from werkzeug.exceptions import BadRequest

user_activity_api_routes = Blueprint('activity_api', __name__)
api = Api(user_activity_api_routes)

BUCKET_NAME = 'givelposts'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'mpeg', 'mp4'])

db = boto3.client('dynamodb')
s3 = boto3.client('s3')

try: 
    try:
        table_response = db.describe_table(TableName='posts')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('Posts Table exists!')
    except:
        posts = create_posts_table()
        print('Posts Table created!')
except:
    pass


# try:
#     try:
#         table_response = db.describe_table(TableName='challenges')
#         if table_response['Table']['TableStatus']:
#             print('Challenges Table exists!')
#     except:
#         challenges = create_challenges_table()
#         print('Challenges Table created!')
# except:
#     pass


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
            response['message'] = 'Success!'
            response['result'] = user['Item']['followers']
        else:
            response['message'] = 'Success!'
            response['message'] = 'You have no followers!'
        return response, 200


class UserPosts(Resource):
    def post(self, user_email):
        """Creates Post"""
        response = {}
        post_data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = datetime.date.today().isoformat()
        time = datetime.datetime.now().strftime("%H:%M:%S")
        user = db.get_item(TableName='users',
                        Key={'email': {'S': user_email}
                        }
                    )
        home_community = user['Item']['home']
        if post_data.get('content') == None and request.files['file'] == None:
            raise BadRequest('Cannot create an empty post!')
        else:
            post = db.put_item(TableName='posts',
                            Item={'user_email': {'S': user_email},
                                 'creation_time': {'S': date_time},
                                 'date': {'S': date},
                                 'time': {'S': time},
                                 'value': {'N': '0'}
                            }
                        )
            if post_data.get('location') != None:
                post = db.update_item(TableName='posts',
                                      Key={'user_email':{'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='SET location = :location',
                                      ExpressionAttributeValues={
                                          ':location': {'S': post_data['location']}
                                      }
                                  )
            else:
                post = db.update_item(TableName='posts',
                                      Key={'user_email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='SET location = :location',
                                      ExpressionAttributeValues={
                                          ':location': {'S': home_community}
                                      }
                                  )
            if post_data.get('content') != None and request.files['file'] == None:
                post = db.update_item(TableName='posts',
                                      Key={'user_email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='SET content = :d',
                                      ExpressionAttributeValues={
                                          ':d': {'S': post_data['content']}
                                      }
                                  )
            elif request.files['file'] != None and post_data.get('content') == None:
                f = request.file['file']
                media_file, file_type = upload_file(f, BUCKET_NAME, user_email+date, ALLOWED_EXTENSIONS)
                if file_type == 'picture_file':
                    post = db.update_item(TableName='posts',
                                          Key={'user_email': {'S': user_email},
                                               'creation_time': {'S': date_time}
                                          },
                                          UpdateExpression='ADD pictures :p',
                                          ExpressionAttributeValues={
                                              ':p': {'SS': [media_file]}
                                          }
                                      )
                elif file_type == 'video_file':
                    post = db.update_item(TableName='posts',
                                          Key={'user_email': {'S': user_email},
                                               'creation_time': {'S': date_time}
                                          },
                                          UpdateExpression='ADD video :v',
                                          ExpressionAttributeValues={
                                              ':v': {'SS': [media_file]}
                                          }
                                      )
            elif post_data.get('content') != None and request.files['file'] != None:
                post = db.update_item(TableName='posts',
                                      Key={'user_email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='SET content = :d',
                                      ExpressionAttributeValues={
                                          ':d': {'S': post_data['content']}
                                      }
                                  )
                response['result']['post_id'] = user_email
                response['result']['post_key'] = date_time
            response['message'] = 'Success! Post Created!'
            return response, 201


        # def put(self, user_email):
        #     """Edit Post"""
        #     response = {}
        #     post_data = request.get_json(force=True)
        #     if 


        # def get(self, user_email):
        #     """Get all user's Posts"""
        #     response = {}
        #     user = db.get_item(TableName='users',
        #                     Key={'email': {'S': user_email}}
        #                 )
        #     if user['Item'].get('following') == None:
        #         response['message'] = 'Success!'
        #         response['result'] = 'You have no followings!'
        #     else:
        #         users_following = user['Item']['following']
        #         for users in users_followings:
        #             following_post = db.query(TableName='posts',
        #                                     Select='ALL_ATTRIBUTES'
        #                                     )



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


