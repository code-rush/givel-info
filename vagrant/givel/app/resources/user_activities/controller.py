import boto3

from app import app

from flask import Blueprint, request, json
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

    