import boto3

dynamodb = boto3.resource('dynamodb')

def create_users_table():
    try:
        users_table = dynamodb.create_table(
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
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
           }
        )
    except:
        try:
            users_table = dynamodb.Table('users')
        except:
            print('Users Table does not exist.')
    finally:
        return users_table


def create_community_table():
    try:
        communities_table = dynamodb.create_table(
            TableName='communities',
            KeySchema=[
                {
                    'AttributeName': 'state',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'city',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    except:
        try:
            communities_table = dynamodb.Table('communities')
        except:
            print('Communities Table does not exist')
    finally:
        return communities_table


def create_posts_table():
    try:
        user_post_table = dynamodb.create_table(
            TableName='posts',
            KeySchema=[
                {
                    'AttributeName': 'user_email',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'creation_time',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'creation_time',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'user_email',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    except:
        try:
            user_post_table = dynamodb.Table('posts')
        except:
            print('Communities Table does not exist')
    finally:
        return user_post_table


def create_challenges_table():
    try:
        challenges_table = dynamodb.create_table(
            TableName='challenges',
            KeySchema=[
                {
                    'AttributeName': 'user_email',
                    'AttributeType': 'HASH'
                },
                {
                    'AttributeName': 'date_time',
                    'AttributeType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'date_time',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    except:
        try:
            challenges_table = dynamodb.Table('challenges')
        except:
            print('challenges table does not exist')
    finally:
        return challenges_table


def create_comments_table():
    try:
        comments_table = dynamodb.create_table(
            TableName='comments',
            KeySchema=[
                {
                    'AttributeName': 'user_email',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'date_time',
                    'KeyType': "RANGE"
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'date_time',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    except:
        try:
            comments_table = dynamodb.Table('comments')
        except:
            print('Comments Table does not exist')
    finally:
        return comments_table
