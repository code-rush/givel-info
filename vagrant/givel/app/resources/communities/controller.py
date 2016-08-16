import boto3

from flask import Blueprint, request, json
from flask_restful import Resource, Api

from app.models import create_community_table

db = boto3.client('dynamodb')

try:
    communities = create_community_table()
    print('Communities table is being created')
except:
    pass



class Communities(Resource):
    def get(self):
        """Returns all communities"""
        communities = db.scan(TableName='communities')
        return communities['Items'], 200
