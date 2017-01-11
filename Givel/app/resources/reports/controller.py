import boto3
import datetime

from app.app import app
from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_report_table

from werkzeug.exceptions import BadRequest


report_activity_api_routes = Blueprint('report_activity_api', __name__)
api = Api(report_activity_api_routes)

db = boto3.client('dynamodb')

try: 
    try:
        table_response = db.describe_table(TableName='reports')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('reports table exists!')
    except:
        reports = create_report_table()
        print('reports table created!')
except:
    pass


class ReportFeeds(Resource):
    def post(self, user_email, feed):
        response = {}
        data = request.get_json(force=True)

        if str(feed) != 'posts' and str(feed) != 'challenges':
            raise BadRequest('Feed can either be posts or challenges')
        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('Provide ID and Key of the feed to report')
        else:
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
            feed_id = str(data['id']) + '_' + str(data['key'])

            try:
                report = db.get_item(TableName='reports',
                                Key={'feed_id': {'S': feed_id},
                                     'reported_by': {'S': user_email}
                                }
                            )

                if report.get('Item') == None:
                    report = db.put_item(TableName='reports',
                                    Item={'feed_id': {'S': feed_id},
                                          'reported_by': {'S': user_email},
                                          'creation_time': {'S': date_time},
                                          'times': {'N': '1'},
                                          'feed': {'S': str(feed)}
                                    }
                                )
                else:
                    report = db.update_item(TableName='reports',
                                Key={'feed_id': {'S': feed_id},
                                     'reported_by': {'S': user_email}
                                },
                                UpdateExpression='SET #t = #t + :i',
                                ExpressionAttributeNames={
                                    '#t': 'times'
                                },
                                ExpressionAttributeValues={
                                    ':i': {'N': '1'}
                                }
                            )
                response['message'] = 'Post Reported!'
            except:
                response['message'] = 'Request failed! Try again later.'

            return response, 200


api.add_resource(ReportFeeds, '/<feed>/<user_email>')




