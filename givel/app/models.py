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
               },
               {
                   'AttributeName': 'home',
                   'AttributeType': 'S'
               },
               {
                   'AttributeName': 'home_away',
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
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'KEYS_ONLY'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 3,
                        'WriteCapacityUnits': 3
                    }
                },
                {
                    'IndexName': 'users-in-home-away-community',
                    'KeySchema': [
                        {
                            'AttributeName': 'home_away',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'KEYS_ONLY'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 3,
                        'WriteCapacityUnits': 3
                    }
                }

            ],
           ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
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
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
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
                },
                {
                    'AttributeName': 'creation_date',
                    'AttributeType': 'S'
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
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                },
                {
                    'IndexName': 'creation-date-time',
                    'KeySchema': [
                        {
                            'AttributeName': 'creation_date',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'creation_time',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 2,
                        'WriteCapacityUnits': 1
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
                },
                {
                    'AttributeName': 'creation_date',
                    'AttributeType': 'S'
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
                        'ReadCapacityUnits': 4,
                        'WriteCapacityUnits': 2
                    }
                },
                {
                    'IndexName': 'creation-date-time',
                    'KeySchema': [
                        {
                            'AttributeName': 'creation_date',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'creation_time',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 2,
                        'WriteCapacityUnits': 1
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
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
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
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
                        'ReadCapacityUnits': 3,
                        'WriteCapacityUnits': 2
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 3
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
                        'ReadCapacityUnits': 3,
                        'WriteCapacityUnits': 3
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
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
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
            }
        )
    except:
        try:
            favorites_table = dynamodb.Table('favorites')
        except:
            print('Favorites Table does not exist')
    finally:
        return favorites_table


def create_report_table():
    try:
        reports_table = dynamodb.create_table(
            TableName='reports',
            KeySchema=[
                {
                    'AttributeName': 'feed_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'reported_by',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'feed_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'reported_by',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 2
            }
        )
    except:
        try:
            reports_table = dynamodb.Table('reports')
        except:
            print('reports Table does not exist')
    finally:
        return reports_table      


def create_organizations_table():
    try:
        organization_table = dynamodb.create_table(
            TableName='organizations',
            KeySchema=[
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'admin_email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'type',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'organizations-admin',
                    'KeySchema': [
                        {
                            'AttributeName': 'admin_email',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'INCLUDE',
                        'NonKeyAttributes': [
                            'password',
                        ]
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 2,
                        'WriteCapacityUnits': 2
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
            }
         )
    except:
        try:
            organization_table = dynamodb.Table('organizations')
        except:
            print('organizations Table does not exist')
    finally:
        return organization_table



def create_shared_feeds_table():
    try:
        shared_feeds_table = dynamodb.create_table(
            TableName='shared_feeds',
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
                    'AttributeName': 'shared_to',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'feed_type',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'share-feeds-shared-to-id',
                    'KeySchema': [
                        {
                            'AttributeName': 'feed_type',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'shared_to',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL',
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 3,
                        'WriteCapacityUnits': 3
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
            }
        )
    except:
        try:
            shared_feeds_table = dynamodb.Table('shared_feeds')
        except:
            print('shared_feeds Table does not exist')
    finally:
        return shared_feeds_table


def create_notifications_table():
    try:
        notifications_table = dynamodb.create_table(
            TableName='notifications',
            KeySchema=[
                {
                    'AttributeName': 'notify_to',
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
                    'AttributeName': 'notify_to',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
            }
         )
    except:
        try:
            notifications_table = dynamodb.Table('notifications')
        except:
            print('notifications Table does not exist')
    finally:
        return notifications_table 


def create_faqs_table():
    try:
        faqs_table = dynamodb.create_table(
             TableName='faqs',
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
                 }
             ],
             ProvisionedThroughput={
                 'ReadCapacityUnits': 2,
                 'WriteCapacityUnits': 2
             }
        )
    except:
        try:
            faqs_table = dynamodb.Table('faqs')
        except:
            print('faqs Table does not exist')
    finally:
        return faqs_table

def create_following_activity_table():
    try:
        following_activity_table = dynamodb.create_table(
            TableName='following_activity',
            KeySchema=[
                {
                    'AttributeName': 'id1',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'id2',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id1',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'id2',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'following',
                    'AttributeType': 'S'
                }
            ],
            LocalSecondaryIndexes=[
                {
                    'IndexName': 'id1-following',
                    'KeySchema': [
                        {
                            'AttributeName': 'id1',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'following',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'id2-following',
                    'KeySchema': [
                        {
                            'AttributeName': 'id2',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'following',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 2,
                        'WriteCapacityUnits': 2
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 2
            }
        )
    except:
        try:
            following_activity_table = dynamodb.Table('following_activity')
        except:
            print('following_activity Table does not exist')
    finally:
        return following_activity_table


def create_challenges_activity_table():
    try:
        challenges_activity_table = dynamodb.create_table(
            TableName='challenges_activity',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'accepted_time',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'accepted_time',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'challenge_id',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'challenge-id-email',
                    'KeySchema': [
                        {
                            'AttributeName': 'challenge_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'email',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 2,
                        'WriteCapacityUnits': 1
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 2
            }
        )
    except:
        try:
            challenges_activity_table = dynamodb.Table('challenges_activity')
        except:
            print('challenges_activity Table does not exist')
    finally:
        return challenges_activity_table

