import boto3

from app.app import app

from flask import Blueprint, request, json
from flask_restful import Resource, Api

from app.models import create_community_table

db = boto3.client('dynamodb')

try:
    table_response = db.describe_table(TableName='communities')
    if table_response['Table']['TableStatus'] == 'ACTIVE':
        print('Communities Table exists!')
    else:
        communities = create_community_table()
        print('Communities table created!')
except:
    pass


community_api_routes = Blueprint('community_api', __name__)
api = Api(community_api_routes)


STATES = {
    'Arizona': 'AZ',
    'California': 'CA',
    'Colorado': 'CO',
    'DC': 'D.C.',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Missouri': 'MO',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Virginia': 'VA',
    'Washington': 'WA',
    'Wisconsin': 'WI',
}


class Communities(Resource):
    def get(self):
        """Returns all communities"""
        communities = db.scan(TableName='communities')
        items = communities['Items']
        response = {}
        for i in items:
            i['state']['S'] = STATES[i['state']['S']]
        response['message'] = 'Success!'
        response['results'] = items
        return response, 200

# class CommunityPosts(Resource):
#     def get(self, user_email):
#         """Returns all posts from users communities"""
#         user_communities = db.get_item(TableName='users',
#                                Key={'email': {'S': user_email}},
#                                ProjectionExpression='home, home_away'
#                            )
#         community_posts = db.scan(TableName='posts',
#                                FilterExpression
#                            )



api.add_resource(Communities, '/')