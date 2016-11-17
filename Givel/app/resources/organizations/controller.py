import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest

from app.models import create_organizations_table

db = boto3.client('dynamodb')

organizations_api_routes = Blueprint('organization_api', __name__)
api = Api(organizations_api_routes)

BUCKET_NAME = 'organizationspicture'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg'])


try: 
    try:
        table_response = db.describe_table(TableName='organizations')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('organizations Table exists!')
    except:
        organizations = create_organizations_table()
        print('organizations Table created!')
except:
    pass


class OrganizationRegistration(Resource):
    """Registers an Organization"""
    def post(self):
        response = {}

        if not request.form['name'] or not request.form['type'] \
          or not request.form['global'] or not request.form['location'] \
          or not request.form['description'] or not request.form['admin'] \
          or not request.form['password']:
            raise BadRequest('Please provide all details.')
        if request.form['type'] != 'b-corp' and request.form['type'] != 'non-profit':
            raise BadRequest('Organization can be either b-corp or non-profit')
        else:
            organization_name = request.form['name']
            organization = db.get_item(TableName='organizations',
                            Key={'name': {'S': organization_name}})
            if organization.get('Item') != None:
                raise BadRequest('Organization with that name already exists.' \
                                 'Please provide a unique organization name.')
            else:
                try:
                    organization = db.put_item(TableName='organizations',
                                        Item={'name': {'S': organization_name},
                                              'description': {'S': request.form['description']},
                                              'type': {'S': request.form['type']},
                                              'global': {'BOOL': request.form['global']},
                                              'location': {'S': request.form['location']},
                                              'admin_email': {'S': request.form['admin']},
                                              'password': {'S': generate_password_hash(request.form['password'])},
                                              'stars': {'N': '0'},
                                              'feed_stars': {'N': '0'},
                                              'comments': {'N': '0'},
                                              'likes': {'N': '0'}
                                        }
                                    )
                    response['message'] = 'Congratulations! Organization registered!'
                except:
                    response['message'] = 'Request Failed! Try again later'
                    return response, 200

                if request.files['picture']:
                    try:
                        f = request.files['picture']
                        picture_file = upload_file(f, BUCKET_NAME, organization_name, ALLOWED_EXTENSIONS)
                        if picture_file != None:
                            user = db.update_item(TableName='users',
                                                Key={'name': {'S': organization_name}},
                                                UpdateExpression='SET picture = :picture',
                                                ExpressionAttributeValues={
                                                         ':picture': {'S': picture_file}}
                                            )
                        response['message'] = 'Congratulations! Organization registered!'
                    except:
                        delete_organization = db.delete_item(TableName='organizations',
                                                Key={'name': {'S': organization_name}})
                        response['message'] = 'Request failed! Try again later'
                        return response, 200

        return response, 201


class ChangeOrganizationName(Resource):
    def put(self):
        response = {}
        data = request.get_json(force=True)

        if data.get('current_name') == None:
            raise BadRequest('Please provide current name of the organization!')
        else:
            organization = db.get_item(TableName='organizations',
                                Key={'name': {'S': data['current_name']}})

            if organization.get('Item') == None:
                raise BadRequest('Organization does not exist!')
            else:
                if data.get('new_name') != None:
                    try:
                        organization = db.update_item(TableName='organizations',
                                        Key={'name': data['current_name']},
                                        UpdateExpression='SET name = :name',
                                        ExpressionAttributeValues={
                                            ':name': {'S': data['new_name']}
                                        }
                                    )
                        response['message'] = 'Organization\'s name changed successfully!'
                    except:
                        response['message'] = 'Request Failed! Try again later'
                else:
                    raise BadRequest('Organization name cannot be empty')

        return response, 200


class ChangeOrganizationDetails(Resource):
    def put(self):
        response = {}
        data = request.get_json(force=True)

        if data.get('name') == None:
            raise BadRequest('Please provide name of the organization!')
        else:
            organization = db.get_item(TableName='organizations',
                                Key={'name': {'S': data['name']}})

            if organization.get('Item') == None:
                raise BadRequest('Organization does not exist!')
            else:
                try:
                    if data.get('type') != None:
                        if data['type'] == 'b-corp' or data['type'] == 'non-profit':
                            organization = db.update_item(TableName='organizations',
                                                Key={'name': {'S': data['name']}},
                                                UpdateExpression='SET type = :t',
                                                ExpressionAttributeValues={
                                                    ':t': {'S': data['type']}
                                                }
                                            )
                        else:
                            raise BadRequest('Type can either be b-corp or non-profit')

                    if data.get('description') != None:
                        organization = db.update_item(TableName='organizations',
                                            Key={'name': {'S': data['name']}},
                                            UpdateExpression='SET description = :d',
                                            ExpressionAttributeValues={
                                                ':d': {'S': data['description']}
                                            }
                                        )

                    if data.get('global') != None:
                        organization = db.update_item(TableName='organizations',
                                            Key={'name': {'S': data['name']}},
                                            UpdateExpression='SET global = :g',
                                            ExpressionAttributeValues={
                                                ':g': {'S': data['global']}
                                            }
                                        )

                    if data.get('location') != None:
                        organization = db.update_item(TableName='organizations',
                                            Key={'name': {'S': data['name']}},
                                            UpdateExpression='SET #loc = :l',
                                            ExpressionAttributeNames={
                                                '#loc': 'location'
                                            },
                                            ExpressionAttributeValues={
                                                ':l': {'S': data['location']}
                                            }
                                        )

                    response['message'] = 'Organization edited successfully!'
                except:
                    response['message'] = 'Request failed! Try again later'

            return response, 200


class OrganizationPicture(Resource):
    def put(self):
        response = {}
        picture = request.files['picture']

        if request.form['name'] == None:
            raise BadRequest('Please provide name of the organization!')
        else:
            organization_name = request.form['name']
            organization = db.get_item(TableName='organizations',
                            Key={'name': {'S': organization_name}})
            if organization.get('Item') != None:
                raise BadRequest('Organization with that name already exists.' \
                                 'Please provide a unique organization name.')
            else:
                try:
                    picture_file = upload_file(picture, BUCKET_NAME, organization_name, ALLOWED_EXTENSIONS)
                    if picture_file != None:
                        pic = db.update_item(TableName='organizations',
                                            Key={'name': {'S': organization_name}},
                                            UpdateExpression='SET picture = :picture',
                                            ExpressionAttributeValues={
                                                     ':picture': {'S': picture_file}}
                                        )
                        response['message'] = 'Picture changed successfully!'
                    else:
                        response ['message'] = 'File not allowed!'
                except:
                    raise BadRequest('Request failed! Try again later')

            return response, 200


class OrganizationLogin(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)

        email = data['email']
        admin = db.query(TableName='organizations',
                        IndexName='organizations-admin',
                        KeyConditionExpression='admin_email = :e',
                        ExpressionAttributeValues={
                            ':e': {'S': email}
                        }
                    )

        if admin.get('Item') != None and check_password_hash(data['password'], \
                                              admin['Item']['password']['S']):
            response['message'] = 'Login successful!'
        else:
            response['message'] = 'Login failed! Try again later!'

        return response, 200


class OrganizationUpliftBillboard(Resource):
    def get(self, organization):
        response = {}
        
        organization = db.get_item(TableName='organizations',
                            Key={'name': {'S': str(organization)}})

        if organization.get('Item') != None:
            org = {}
            org['picture'] = organization['picture']['S']
            org['description'] = organization['description']['S']
            org['name'] = organization['name']['S']
            org['stars'] = organization['stars']
            if organization['global']['BOOL'] == False:
                org['location'] = {}
                org['location']['S'] = 'global'
            else:
                org['location'] = organization['location']
            if organization['type']['S'] == 'b-corp':
                org['type']['S'] = 'social good'
            else:
                org['type'] = organization['type']

            response['results'] = org
            response['message'] = 'Successful fetched organizations uplift billboard!'
        else:
            response['message'] = 'Organization does not exist!'

        return response, 200


class OrganizationFeedBillboard(Resource):
    def get(self, organizations):
        response = {}

        organization = db.get_item(TableName='organizations',
                            Key={'name': {'S': str(organization)}})

        if organization.get('Item') != None:
            org = {}
            org['picture'] = organization['picture']['S']
            org['description'] = organization['description']['S']
            org['name'] = organization['name']['S']
            if organization['global']['BOOL'] == False:
                org['location'] = {}
                org['location']['S'] = 'global'
            else:
                org['location'] = organization['location']
            if organization['type']['S'] == 'b-corp':
                org['type']['S'] = 'social good'
            else:
                org['type'] = organization['type']
            org['comments'] = organization['comments']
            org['likes'] = organization['likes']
            org['stars'] = organization['feed_stars']

            response['results'] = org
            response['message'] = 'Successful fetched organizations uplift billboard!'
        else:
            response['message'] = 'Organization does not exist!'

        return response, 200


class OrganizationUpliftStats(Resource):
    def get(self, organization):
        response = {}

        organization = db.get_item(TableName='organizations',
                            Key={'name': {'S': str(organization)}})

        all_organizations_stars = db.scan(TableName='organizations',
                                    ProjectionExpression='stars')

        total_organization_stars = 0

        for stars in all_organizations_stars['Items']:
            total_organization_stars += int(stars['stars']['N'])

        avg_stars_of_other_organizations = (total_organization_stars / \
                                            int(all_organizations_stars['count']))

        org_stats = (int(organization['stars']['N']) / \
                      avg_stars_of_other_organizations + \
                      int(organization['stars']['N'])) * 100

        other_org_stats = (avg_stars_of_other_organizations / \
                           avg_stars_of_other_organizations + \
                           int(organization['stars']['N'])) * 100


        response['message'] = 'Request successful!'
        response['result'] = {}
        response['result']['organization_stars_percentage'] = {}
        response['result']['other_organizations_stars_percentage'] = {}
        response['result']['organization_stars_percentage']['S'] = str(org_percent_stats)
        response['result']['other_organizations_stars_percentage']['S'] = str(other_org_stats)

        return response, 200


class OrganizationFeedStats(Resource):
    def get(self, organization):
        response = {}

        organization = db.get_item(TableName='organizations',
                            Key={'name': {'S': str(organization)}})

        all_organizations_feed_stars = db.scan(TableName='organizations',
                                          ProjectionExpression='feed_stars')

        total_org_feed_stars = 0

        for stars in all_organizations_feed_stars['Items']:
            total_org_feed_stars += int(stars ['feed_stars']['N'])

        avg_stars_of_other_org = (total_org_feed_stars / \
                                  int(all_organizations_stars['count']))

        org_stats = (int(organization['feed_stars']['N'])/ \
                     avg_stars_of_other_org + \
                      int(organization['feed_stars']['N'])) * 100

        other_org_stats = (avg_stars_of_other_org / \
                           avg_stars_of_other_org + \
                           int(organization['feed_stars']['N'])) * 100

        response['message'] = 'Request successful!'
        response['result'] = {}
        response['result']['organization_stars_percentage'] = {}
        response['result']['other_organizations_stars_percentage'] = {}
        response['result']['organization_stars_percentage']['S'] = str(org_stats)
        response['result']['other_organizations_stars_percentage']['S'] = str(other_org_stats)
        return response, 200



api.add_resource(OrganizationRegistration, '/register')
api.add_resource(OrganizationLogin, '/login')
api.add_resource(ChangeOrganizationDetails, '/settings/details')
api.add_resource(ChangeOrganizationName, '/settings/name')
api.add_resource(OrganizationPicture, '/settings/picture')
