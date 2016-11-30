import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from werkzeug.exceptions import BadRequest

from app.helper import STATES, mid_west_states, southeast_states, northeast_states
from app.helper import pacific_states, southwest_states, rocky_mountain_states

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


class GiveStarsOnUplift(Resource):
    def post(self, user_email):
        response = {}
        data = request.get_json(force=True)

        user = db.get_item(TableName='users',
                        Key={'email': {'S': user_email}},
                        ConsistentRead=True
                    )

        if int(user['Item']['givel_stars']['N']) == 0:
            raise BadRequest('You have no stars left to donate.')
        else:
            if int(data['stars']) == 0:
                raise BadRequest('Cannot donate less than 1 star.')
            if int(user['Item']['givel_stars']['N']) < int(data['stars']):
                raise BadRequest('You don\'t have enough stars to donate.')
            if data.get('organizations_name') == None:
                raise BadRequest('Please provide organizations name to give stars to.')

            st = user['Item']['home']['S'].rsplit(' ', 1)[1]
            region = None

            if STATES[st] in pacific_states:
                region = 'pacific_region_stars'
            elif STATES[st] in southwest_states:
                region = 'south_west_region_stars'
            elif STATES[st] in mid_west_states:
                region = 'mid_west_region_stars'
            elif STATES[st] in rocky_mountain_states:
                region = 'rocky_mountain_region_stars'
            elif STATES[st] in southeast_states:
                region = 'south_east_region_stars'
            elif STATES[st] in northeast_states:
                region = 'north_east_region_stars'

            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if data.get('stars') != None:
                try:
                    star_post = db.put_item(TableName='stars_activity',
                                    Item={'email': {'S': user_email},
                                          'shared_time': {'S': date_time},
                                          'stars': {'N': str(data['stars'])},
                                          'shared_to': {'S': 'organization'},
                                          'shared_id': {'S': data['organizations_name']}
                                    }
                                )
                except:
                    raise BadRequest('Request Failed!')

                try:
                    add_stars_to_organization = db.update_item(TableName='organizations',
                                        Key={'name': {'S': data['organizations_name']}},
                                        UpdateExpression='SET stars = stars + :s, \
                                                          SET #rs = #rs + :s',
                                        ExpressionAttributeNames={
                                            '#rs': region
                                        },
                                        ExpressionAttributeValues={
                                            ':s': {'N': str(data['stars'])}
                                        }
                                    )

                    deduct_users_stars = db.update_item(TableName='users',
                                        Key={'email': {'S': user_email}},
                                        UpdateExpression='SET givel_stars = givel_stars - :s, \
                                                    total_stars_shared = total_stars_shared + :s',
                                        ExpressionAttributeValues={
                                            ':s': {'N': str(data['stars'])}
                                        }
                                    )

                    response['message'] = 'Stars shared successfully'
                except:
                    result['message'] = 'Request failed! Try again later'

            return response, 200



api.add_resource(OrganizationsUplift, '/<type>')
api.add_resource(GiveStarsOnUplift, '/stars/share/<user_email>')

