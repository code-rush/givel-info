import boto3

from app import app

from flask import Blueprint, request
from flask_restful import Api, Resource


user_activities_api_routes = Blueprint('activity_api', __name__)
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
                        UpdateExpression='ADD followers = :followers',
                        ExpressionAttributeValues={
                            ':followers': {'SS': [user_email]}
                        }
                    )
        return 200