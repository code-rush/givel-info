import boto3

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from werkzeug.exceptions import BadRequest

organizations_uplift_api_routes = Blueprint('uplift_api_routes', __name__)
api = Api(organizations_uplift_api_routes)


db = boto3.client('dynamodb')


class OrganizationsUplift(Resource):
    def get(self, o_type):
        response = {}

        if str(o_type) != 'social_good' and str(o_type) != 'non-profit':
            raise BadRequest('Organizations type can be either social_good or non-profit.')
        else:
            type = None
            if str(o_type) == 'social_good':
                type = 'b-corp'
            else:
                type = 'non-profit'
            organizations = db.query(TableName='organizations',
                                  IndexName='organizations-type-name',
                                  KeyConditionExpression='type = :t',
                                  ExpressionAttributeValues={
                                      ':t': {'S': type}
                                  }
                              )

            organizations = []

            if organizations.get('Items') == []:
                response['message'] = 'No organizations exists currently'
            else:
                for organization in organizations['Items']:
                    del organization['admin_email']
                    del organization['password']
                    del organization['type']
                    organizations.append(organization)
                response['message'] = 'Successfully fetched all organizations'
                response['result'] = organizations

            return response, 200



api.add_resource(OrganizationsUplift, '/<type>')

