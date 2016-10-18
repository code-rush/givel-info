import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

user_following_activity_api_routes = Blueprint('following_activity_api', __name__)
api = Api(user_following_activity_api_routes)

db = boto3.client('dynamodb')


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

        

api.add_resource(UserFollowing, '/<user_email>/following')
api.add_resource(UserFollowers, '/<user_email>/followers')
