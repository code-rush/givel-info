import boto3

from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
app.config['AWS_ACCESS_KEY_ID'] = YOUR_ACCESS_KEY
app.config['AWS_SECRET_ACCESS_KEY'] = YOUR_SECRET_ACCESS_KEY

# Testing on local database
app.config['DYNAMO_ENABLE_LOCAL'] = True
app.config['DYNAMO_LOCAL_HOST'] = 'localhost'
app.config['DYNAMO_LOCAL_PORT'] = 8000

dynamodb = boto3.resource('dynamodb')

user_table = dynamodb.create_table(
	TableName='users',
	KeySchema=[
		{
		'AttributeName': 'email',
		'KeyType': 'HASH'
		}
	],
	AttributeDefinitions=[
		{
			'AttributeName': 'email',
			'AttributeType': 'S'
		}
	],
	ProvisionedThroughput={
		'ReadCapacityUnits': 5,
		'WriteCapacityUnits': 5
	}
)

class HelloWorld(Resource):
	def get(self):
		return {'Hello': 'HelloWorld'}


api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
	app.run(debug=True)