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
           GlobalSecondaryIndexes=[
                {
                    'IndexName': 'users-in-home-community',
                    'KeySchema': [
                        {
                            'AttributeName': 'home',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'email',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'KEYS_ONLY'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 10
                    }
                },
                {
                    'IndexName': 'users-in-home-away-community',
                    'KeySchema': [
                        {
                            'AttributeName': 'home_away',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'email',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'KEYS_ONLY'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 10
                    }
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
                    'AttributeName': 'email',
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
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'value',
                    'AttributeType': 'N'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'post-value-email',
                    'KeySchema': [
                        {
                            'AttributeName': 'value',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'email',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 10
                    }
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
            print('posts Table does not exist')
    finally:
        return user_post_table


def create_challenges_table():
    try:
        challenges_table = dynamodb.create_table(
            TableName='challenges',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'creation_time',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'creation_time',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'value',
                    'AttributeType': 'N'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'challenge-value-email',
                    'KeySchema': [
                        {
                            'AttributeName': 'value',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'email',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 10
                    }
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


def create_likes_table():
    try:
        likes_table = dynamodb.create_table(
            TableName='likes',
            KeySchema=[
                {
                    'AttributeName': 'feed',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'user',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'feed',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except:
        try:
            likes_table = dynamodb.Table('likes')
        except:
            print('likes table does not exist')
    finally:
        return 


def create_stars_activity_table():
    try:
        stars_table = dynamodb.create_table(
            TableName='stars_activity',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'shared_time',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'shared_time',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'shared_to',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'shared_id',
                    'AttributeType': 'S'
                }
            ],
            LocalSecondaryIndexes=[
                {
                    'IndexName': 'personal-sharing-accounts',
                    'KeySchema': [
                        {
                            'AttributeName': 'email',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'shared_to',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'stars-activity-email-id',
                    'KeySchema': [
                        {
                            'AttributeName': 'email',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'shared_id',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'KEYS_ONLY'
                    }
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'shared-to-id',
                    'KeySchema': [
                        {
                            'AttributeName': 'shared_to',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'shared_id',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 10
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except:
        try:
            stars_table = dynamodb.Table('stars_activity')
        except:
            print('stars table does not exist')
    finally:
        return stars_table


def create_comments_table():
    try:
        comments_table = dynamodb.create_table(
            TableName='comments',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'creation_time',
                    'KeyType': "RANGE"
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'creation_time',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'feed_id',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'comments-feed-email',
                    'KeySchema': [
                        {
                            'AttributeName': 'feed_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'email',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 10
                    }
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


def create_favorite_posts_table():
    try:
        favorites_table = dynamodb.create_table(
            TableName='favorites',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'feed_id',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'feed_id',
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
            favorites_table = dynamodb.Table('favorites')
        except:
            print('Favorites Table does not exists')
    finally:
        return favorites_table
