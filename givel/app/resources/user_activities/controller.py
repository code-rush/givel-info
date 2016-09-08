import boto3
# import datetime

from app import app

from flask import Blueprint, request
from flask_restful import Api, Resource


user_activity_api_routes = Blueprint('activity_api', __name__)
api = Api(user_activity_api_routes)

db = boto3.client('dynamodb')

try: 
    posts = create_post_table()
except:
    pass


class UserFollowingActivities(Resource):
    def get(self, user_email):
        """Returns list of users followings"""
        user = db.get_item(
                    TableName='users',
                    Key={'email': {'S': user_email}}
                )
        return user['Item']['following'], 200

    def put(self, user_email):
        """Adds a user to the following and followers list"""
        data = request.get_json(force=True)
        if data['follow_user']:
            user = db.update_item(
                        TableName='users',
                        Key={'email': {'S': user_email}},
                        UpdateExpression='ADD following = :following',
                        ExpressionAttributeValues={
                            ':following': {'SS': [data['follow_user']]}
                        }
                    )
            user_following = db.update_item(
                        TableName='users',
                        Key={'email': {'S': data['follow_user']}},
                        UpdateExpression='ADD followers = :follower',
                        ExpressionAttributeValues={
                            ':follower': {'SS': [user_email]}
                        }
                    )
        return 200

    def delete(self, user_email):
        """Unfollows a user"""
        data = request.get_json(force=True)
        if data['unfollow_user']:
            user = db.update_item(
                        TableName='users',
                        Key={'email': {'S': user_email}},
                        UpdateExpression='DELETE :user',
                        ExpressionAttributeValues={
                            ':user': {'SS':[data['unfollow_user']]}
                        }
                    )
            user_following = db.update_item(
                        TableName='users',
                        Key={'email': {'S': data['unfollow_user']}},
                        UpdateExpression='DELETE :follower',
                        ExpressionAttributeValues={
                            ':follower': {'SS':[user_email]}
                        }
                    )
        return 200


class UserFollowers(Resource):
    def get(self, user_email):
        """Returns list of followers"""
        user = db.get_item(
                        TableName='users',
                        Key={'email': {'S': user_email}}
                    )
        return user['Item']['followers'], 200


class UserPosts(Resource):
    def post(self, user_email):
        """Creates User Posts"""
        post_data = request.get_json(force=True)
        post = db.put_item(TableName='posts',
                           Item={'user_email': {'S': user_email},
                                'date_time': {'S': post_data['date_time']}
                           }
                      )
        if post_data['description']:
            post = db.update_item(TableName='posts',
                                  Key={'user_email': {'S': user_email},
                                       'date_time': {'S': post_data['date_time']}
                                  },
                                  UpdateExpression='SET description = :d',
                                  ExpressionAttributeValues={
                                      ':d': {'S': post_data['description']}
                                  }
                              )
        if post_data['picture']:
            post = db.update_item(TableName='posts',
                                  Key={'user_email': {'S': user_email},
                                       'date_time': {'S': post_data['date_time']}
                                  },
                                  UpdateExpression='SET picture = :p',
                                  ExpressionAttributeValues={
                                      ':p': {'S': post_data['picture']}
                                  }
                              )
        if post_data['video']:
            post = db.update_item(TableName='posts',
                                  Key={'user_email': {'S': user_email},
                                       'date_time': {'S': post_data['date_time']}
                                  },
                                  UpdateExpression='SET video = :v',
                                  ExpressionAttributeValues={
                                      ':v': {'S': post_data['video']}
                                  }
                              )


api.add_resource(UserFollowingActivities, '/<user_email>/following')
api.add_resource(UserFollowers, '/<user_email>/followers')


