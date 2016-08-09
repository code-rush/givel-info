import boto3

from app import app

from flask import Blueprint, request
from flask_restful import Api, Resource


user_activity_api_routes = Blueprint('activity_api', __name__)
api = Api(user_activities_api_routes)

db = boto3.client('dynamodb')


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



api.add_resource(UserFollowingActivities, '/<user_email>/following')
api.add_resource(UserFollowers, '/<user_email>/followers')


