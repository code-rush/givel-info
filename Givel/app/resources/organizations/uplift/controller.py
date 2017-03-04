import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from werkzeug.exceptions import BadRequest

from app.helper import (STATES, mid_west_states, southeast_states, 
                        northeast_states, pacific_states, southwest_states,
                        rocky_mountain_states, check_if_user_following_user,
                        check_if_post_added_to_favorites,
                        check_if_user_exists, check_if_user_starred)

organizations_uplift_api_routes = Blueprint('uplift_api_routes', __name__)
api = Api(organizations_uplift_api_routes)


db = boto3.client('dynamodb')


class UpliftOrganizationsFeed(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user_id.')

        if data.get('last_evaluated_key') != None:
            organizations = db.scan(TableName='organizations',
                                Limit=50,
                                ExclusiveStartKey=data['last_evaluated_key']
                            )
        else:
            organizations = db.scan(TableName='organizations',
                                Limit=50
                            )

        orgs = []

        if organizations.get('LastEvaluatedKey') != None:
            response['last_evaluated_key'] = organizations['LastEvaluatedKey']

        try:
            for org in organizations['Items']:
                org['id'] = org['name']
                del org['admin_email']
                del org['password']
                del org['type']
                del org['likes']
                del org['comments']
                del org['feed_stars']
                del org['mid_west_region_stars']
                del org['mid_west_region_feed_stars']
                del org['north_east_region_stars']
                del org['north_east_region_feed_stars']
                del org['pacific_region_stars']
                del org['pacific_region_feed_stars']
                del org['rocky_mountain_region_stars']
                del org['rocky_mountain_region_feed_stars']
                del org['south_east_region_stars']
                del org['south_east_region_feed_stars']
                del org['south_west_region_stars']
                del org['south_west_region_feed_stars']
                del org['stars']
                del org['location']
                del org['link']
                del org['global']

                orgs.append(org)

            response['message'] = 'Request successful.'
            response['result'] = orgs
        except:
            raise BadRequest('Request failed. Please try again later.')
    
        return response, 200


class GetOrganizationsFeed(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user_id.')
        if data.get('organization_id') == None:
            raise BadRequest("Please provide organization's id.")

        user_exists = check_if_user_exists(data['user_id'])
        if not user_exists:
            raise BadRequest('User does not exist. '\
                             + 'Please register the user.')

        organization = db.get_item(TableName='organizations',
                                Key={'name': {'S': data['organization_id']}})

        following = check_if_user_following_user(data['user_id'],
                                        organization['Item']['name']['S'])
        feed_id = 'organization_' + organization['Item']['name']['S']
        added_to_fav = check_if_post_added_to_favorites(feed_id, 
                                                data['user_id'])
        starred = check_if_user_starred(organization['Item']['name']['S'],
                                                        data['user_id'])

        if organization['Item']['type']['S'] == 'b-corp':
            o_type = 'social good'
        else:
            o_type = 'non profit'
        org = {}
        org['organization'] = {}
        org['organization']['id'] = organization['Item']['name']
        org['organization']['name'] = organization['Item']['name']
        org['organization']['description'] = organization['Item']['description']
        org['organization']['picture'] = organization['Item']['picture']
        org['organization']['type'] = {}
        org['organization']['type']['S'] = o_type
        org['feed'] = {}
        org['feed']['id'] = {}
        org['feed']['id']['S'] = 'organization'
        org['feed']['key'] = organization['Item']['name']
        org['following'] = {}
        org['following']['BOOL'] = following
        org['added_to_fav'] = {}
        org['added_to_fav']['BOOL'] = added_to_fav
        org['stars'] = organization['Item']['stars']
        org['location'] = organization['Item']['location']
        org['global'] = organization['Item']['global']
        org['starred'] = {}
        org['starred']['BOOL'] = starred
        org['link'] = organization['Item']['link']

        response['message'] = 'Request successful.'
        response['result'] = org

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
            if data.get('organization_name') == None:
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

            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

            if data.get('stars') != None:
                try:
                    star_post = db.put_item(TableName='stars_activity',
                                    Item={'email': {'S': user_email},
                                          'shared_time': {'S': date_time},
                                          'stars': {'N': str(data['stars'])},
                                          'shared_to': {'S': 'organization'},
                                          'shared_id': {'S': data['organization_name']}
                                    }
                                )
                    add_stars_to_organization = db.update_item(TableName='organizations',
                                        Key={'name': {'S': data['organization_name']}},
                                        UpdateExpression='SET stars = stars + :s, \
                                                          #rs = #rs + :s',
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
                    raise BadRequest('Request failed! Please try again later.')

            return response, 200



api.add_resource(UpliftOrganizationsFeed, '/')
api.add_resource(GetOrganizationsFeed, '/feed')
api.add_resource(GiveStarsOnUplift, '/stars/share/<user_email>')

