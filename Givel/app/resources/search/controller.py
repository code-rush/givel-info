import boto3

from app.app import app
from flask import Blueprint, request
from flask_restful import Api, Resource

from app.helper import get_user_details, check_if_user_following_user

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

        search_results = []
        if data.get('search_for') != None:
            results = None
            if '@' in data['search_for']:
                results = users_table.query(Select='ALL_ATTRIBUTES',
                            KeyConditionExpression=Key('email').eq(data['search_for'].lower())
                        )
            else:
                search_upper = data['search_for'].upper()
                search_lower = data['search_for'].lower()
                if len(data['search_for']) > 1:
                    search_camel = data['search_for'][0].upper() + data['search_for'][1:].lower()
                    results = users_table.scan(Select='ALL_ATTRIBUTES',
                            FilterExpression=Attr('first_name').begins_with(search_lower) \
                                            | Attr('last_name').begins_with(search_lower) \
                                            | Attr('first_name').begins_with(search_upper) \
                                            | Attr('last_name').begins_with(search_upper) \
                                            | Attr('first_name').begins_with(search_camel) \
                                            | Attr('last_name').begins_with(search_camel)
                              )
                else:
                    results = users_table.scan(Select='ALL_ATTRIBUTES',
                            FilterExpression=Attr('first_name').begins_with(search_lower) \
                                            | Attr('last_name').begins_with(search_lower) \
                                            | Attr('first_name').begins_with(search_upper) \
                                            | Attr('last_name').begins_with(search_upper)
                              )

            if results.get('Count') != None:
                if results['Count'] == 0:
                    response['message'] = 'No user found with that name'
                else:
                    response['message'] = 'Successfully found the following matches'
                    for item in results['Items']:
                        if item['email'] != user_email:
                            following_user = check_if_user_following_user(user_email, 
                                                                        item['email'])
                            users = {}
                            users['name'] = {}
                            users['name']['S'] = item['first_name'] + ' ' \
                                                    + item['last_name']
                            users['home_community'] = {}
                            users['home_community']['S'] = item['home']
                            users['id'] = {}
                            users['id']['S'] = item['email']
                            users['following'] = {}
                            users['following']['BOOL'] = following_user
                            
                            if item.get('profile_picture') != None:
                                users['profile_picture'] = {}
                                users['profile_picture']['S'] = item['profile_picture']

                            if following_user == True:
                                search_results.insert(0, users)
                            else:
                                search_results.append(users)
                    response['results'] = search_results
        else:
            response['message'] = 'Please provide some input!'

        return response, 200


api.add_resource(SearchUsersOnGivel, '/users/<user_email>')
