import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Resource, Api

from app.models import create_faqs_table

from werkzeug.exceptions import BadRequest

db = boto3.client('dynamodb')

try: 
    try:
        table_response = db.describe_table(TableName='faqs')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('FAQs Table exists!')
    except:
        faq = create_faqs_table()
        print('FAQs Table created!')
except:
    pass


faq_api_routes = Blueprint('faqs_api', __name__)
api = Api(faq_api_routes)


class AskQuestion(Resource):
    def post(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('question') == None:
            raise BadRequest('Please ask a question.')
        else:
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            put_question = db.put_item(TableName='faqs',
                                Item={'email': {'S': str(user_email)},
                                      'creation_time': {'S': date_time},
                                      'question': {'S': data['question']}
                                }
                            )

            response['message'] = 'Successfully posted a question!'

        return response, 201

class GetFAQs(Resource):
    def get(self):
        response = {}

        try:
            faqs = db.scan(TableName='QAs')

            response['message'] = 'Request successful!'
            response['result'] = faqs['Items']
            return response, 200
        except:
            raise BadRequest('Request failed! Please try again later')


api.add_resource(AskQuestion, '/question/<user_email>')
api.add_resource(GetFAQs, '/')