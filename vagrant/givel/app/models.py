import boto3

dynamodb = boto3.resource('dynamodb')

users = dynamodb.create_table(
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

community = dynamodb.create_table(
    TableName='community',
    KeySchema=[
      {
          'AttributeName': 'name',
          'KeyType': 'HASH'
      }
   ],
   AttributeDefinitions=[
      {
          'AttributeName': 'name',
          'AttributeType': 'S',
      }
   ],
   ProvisionedThroughput={
      'ReadCapacityUnits': 5,
      'WriteCapacityUnits': 5
   }
)