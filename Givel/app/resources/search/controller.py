import boto3

from app.app import app
from flask import Blueprint, request
from flask_restful import Api, Resource

from app.helper import get_user_details

from werkzeug.exceptions import BadRequest

from boto3.dynamodb.conditions import Key, Attr

search_api_routes = Blueprint('search_api', __name__)
api = Api(search_api_routes)


db = boto3.client('dynamodb')

dynamo = boto3.resource('dynamodb')

users_table = dynamo.Table('users')

class SearchUsersOnGivel(Resource):
    def post(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('search_for') != None:
            results = users_table.scan(Select='ALL_ATTRIBUTES',
                        FilterExpression=Attr('first_name').begins_with(data['search_for']) \
                                        | Attr('last_name').begins_with(data['search_for'])
                          )

            if results['Count'] == 0:
                response['message'] = 'No user found with that name'
            else:
                response['message'] = 'Succefully found the following matches'
                for item in results['Items']:
                    user_name, profile_picture, home = get_user_details(item['email'])
                    if user_name == None:
                        del item
                    else:
                        users = {}
                        users['name'] = {}
                        users['profile_picture'] = {}
                        users['name']['S'] = user_name
                        users['profile_picture']['S'] = profile_picture
                        response['results'] = users
        else:
            response['message'] = 'Please provide some input!'

        return response, 200


api.add_resource(SearchUsersOnGivel, '/users/<user_email>')
