import boto3

from app import app

from flask import Blueprint, request, json
from flask_restful import Resource, Api

from app.models import create_community_table

db = boto3.client('dynamodb')

try:
    communities = create_community_table()
    print('Communities table is being created')
except:
    pass


community_api_routes = Blueprint('community_api', __name__)
api = Api(community_api_routes)


class Communities(Resource):
    def get(self):
        """Returns all communities"""
        communities = db.scan(TableName='communities')
        items = communities['Items']
        results = {}
        for i in items:
            results[i['city']['S']] = i['state']['S']
        return results, 200


api.add_resource(Communities, '/')