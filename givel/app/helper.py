import boto3
import datetime

s3 = boto3.client('s3')
db = boto3.client('dynamodb')

IMAGE = set(['jpg', 'png', 'jpeg'])
VIDEO = set(['mp4', 'mpeg', 'MOV', 'mov'])
STATES = {
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'DC': 'D.C.',
    'FL': 'Florida',
    'GA': 'Georgia',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WI': 'Wisconsin',
}

pacific_states = ['California', 'Oregon', 'Washington']
southwest_states = ['Arizona', 'Texas', 'Oklahoma', 'New Mexico']
rocky_mountain_states = ['Nevada', 'Utah', 'Colorado', \
                        'Idaho', 'Montana', 'Wyoming']
mid_west_states = ['North Dakota', 'South Dakota', 'Nebraska', 'Kansas', \
                   'Minnesota', 'Missouri', 'Iowa', 'Wisconsin', 'Illinois',\
                   'Indiana', 'Michigan', 'Ohio']
southeast_states = ['Tennessee', 'Arkansas', 'Louisiana', 'Kentucky', \
                    'Mississippi', 'Alabama', 'Georgia', 'West Virginia', \
                    'Virginia', 'North Carolina', 'South Carolina', 'Florida']
northeast_states = ['Pennsylvania', 'New York', 'Maryland', 'Vermont', \
                    'New Hampshire', 'Maine', 'Massachusetts', 'Connecticut', \
                    'Rhode Island', 'New Jersey']

APP_DATE = '2016-12-31'

def check_if_user_exists(user_id):
    user = db.get_item(TableName='users',
                      Key={'email': {'S': user_id}})
    if user.get('Item') != None:
        return True
    else:
        return False

def upload_file(file, bucket, key, extensions):
    if file and allowed_file(file.filename, extensions):
        filename = str(bucket)+'.s3.amazonaws.com/'+str(key)
        upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='image/jpeg'
                        )
        return filename
    else:
        return None

def upload_post_file(file, bucket, key, extensions):
    if file and allowed_file(file.filename, extensions):
        file_type = type_of_file(file.filename)
        filename = str(bucket)+'.s3.amazonaws.com/'+str(key)
        if file_type == 'picture_file':
            upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='image/jpeg'
                        )
        if file_type == 'video_file':
            upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='audio/mpeg'
                        )
        return filename, file_type
    else:
        return None


def allowed_file(filename, extensions):
    """Checks if the file is allowed to upload"""
    return '.' in filename and filename.rsplit('.', 1)[1] in extensions


def type_of_file(filename):
    """Returns type of media file"""
    format = filename.rsplit('.', 1)[1]
    if format in IMAGE:
        return 'picture_file'
    else:
        return 'video_file'


def check_if_community_exists(community):
    """Returns city, state and True if community exists"""
    comm = community.rsplit(' ', 1)
    state = comm[1]
    city = comm[0][:-1]
    exist = False
    response = db.query(TableName='communities', 
                        KeyConditionExpression='#s = :s and city = :c',
                        ExpressionAttributeNames={
                            '#s': 'state' 
                        },
                        ExpressionAttributeValues={
                            ':s': {'S': state},
                            ':c': {'S': city}
                        }
                    )

    if response.get('Items') != []:
        exist = True
    return city, state, exist


def update_member_counts(city, state, operation):
    """Updates Member Counts"""
    if operation == 'add':
        update_count = db.update_item(TableName='communities',
                                    Key={'state': {'S': state},
                                         'city': {'S': city},
                                    },
                                    UpdateExpression='SET members = members + :m',
                                    ExpressionAttributeValues={
                                        ':m': {'N': '1'}
                                    }
                                )
    elif operation == 'remove':
        update_count = db.update_item(TableName='communities',
                                    Key={'state': {'S': state},
                                         'city': {'S': city},
                                    },
                                    UpdateExpression='SET members = members - :m',
                                    ExpressionAttributeValues={
                                        ':m': {'N': '1'}
                                    }
                                )


def update_likes(feed, id, key, operation):
    if id == 'organization':
        if operation == 'like':
            update_count = db.update_item(TableName='organizations',
                                Key={'name': {'S': key}},
                                UpdateExpression='SET likes = likes + :l',
                                ExpressionAttributeValues={
                                    ':l': {'N': '1'}
                                }
                            )
        elif operation == 'unlike':
            update_count = db.update_item(TableName='organizations',
                                Key={'name': {'S': key}},
                                UpdateExpression='SET likes = likes - :l',
                                ExpressionAttributeValues={
                                    ':l': {'N': '1'}
                                }
                            )
    else:
        if operation == 'like':
            update_count = db.update_item(TableName=feed,
                                    Key={'email': {'S': id},
                                         'creation_time': {'S': key}
                                    },
                                    UpdateExpression='SET likes = likes + :l',
                                    ExpressionAttributeValues={
                                        ':l': {'N': '1'}
                                    }
                                )
        elif operation == 'unlike':
            update_count = db.update_item(TableName=feed,
                                    Key={'email': {'S': id},
                                         'creation_time': {'S': key}
                                    },
                                    UpdateExpression='SET likes = likes - :l',
                                    ExpressionAttributeValues={
                                        ':l': {'N': '1'}
                                    }
                                )

def update_stars_count(feed, id, key, stars=None):
    if id == 'organization':
        update_count = db.update_item(TableName=feed,
                        Key={'name': {'S': key}},
                        UpdateExpression='SET feed_stars = feed_stars + :s',
                        ExpressionAttributeValues={
                           ':s': {'N': stars}
                        }
                    )
    else:
        update_count = db.update_item(TableName=feed,
                        Key={'email': {'S': id},
                             'creation_time': {'S': key}},
                        UpdateExpression='SET stars = stars + :s',
                        ExpressionAttributeValues={
                           ':s': {'N': stars}
                        }
                    )

def update_comments(id, key, operation):
    if id == 'organization':
        if operation == 'add_comment':
            update_count = db.update_item(TableName='organization',
                            Key={'name': {'S': key}},
                            UpdateExpression='SET comments = comments + :c',
                            ExpressionAttributeValues={
                                ':c': {'N': '1'}
                            }
                        )
        elif operation == 'delete_comment':
            update_count = db.update_item(TableName='organization',
                            Key={'name': {'S': key}},
                            UpdateExpression='SET comments = comments - :c',
                            ExpressionAttributeValues={
                                ':c': {'N': '1'}
                            }
                        )
    else:
        get_feed = db.get_item(TableName='posts',
                        Key={'email': {'S': id},
                             'creation_time': {'S': key}
                        }
                    )
        if get_feed.get('Item') != None:
            feed_type = 'posts'
        else:
            feed_type = 'challenges'

        if operation == 'add_comment':
            update_count = db.update_item(TableName=feed_type,
                            Key={'email': {'S': id},
                                 'creation_time': {'S': key}
                            },
                            UpdateExpression='SET comments = comments + :c',
                            ExpressionAttributeValues={
                                ':c': {'N': '1'}
                            }
                        )
        elif operation == 'delete_comment':
            update_count = db.update_item(TableName=feed_type,
                            Key={'email': {'S': id},
                                 'creation_time': {'S': key}
                            },
                            UpdateExpression='SET comments = comments - :c',
                            ExpressionAttributeValues={
                                ':c': {'N': '1'}
                            }
                        )

def update_value(feed, id, key, operation, stars=None):
    if id == 'organization':
        return
    else:
        if operation == 'like':
            update_count = db.update_item(TableName=feed,
                                    Key={'email': {'S': id},
                                         'creation_time': {'S': key}
                                    },
                                    UpdateExpression='SET #val = #val + :v',
                                    ExpressionAttributeNames={
                                        '#val': 'value'
                                    },
                                    ExpressionAttributeValues={
                                        ':v': {'N': '1'}
                                    }
                                )
        elif operation == 'unlike':
            update_count = db.update_item(TableName=feed,
                                    Key={'email': {'S': id},
                                         'creation_time': {'S': key}
                                    },
                                    UpdateExpression='SET #val = #val - :v',
                                    ExpressionAttributeNames={
                                        '#val': 'value'
                                    },
                                    ExpressionAttributeValues={
                                        ':v': {'N': '1'}
                                    }
                                )
        elif operation == 'stars':
            if stars != None:
                value = str(int(stars) * 5)
                update_count = db.update_item(TableName=feed,
                                        Key={'email': {'S': id},
                                             'creation_time': {'S': key}
                                        },
                                        UpdateExpression='SET #val = #val + :v',
                                        ExpressionAttributeNames={
                                            '#val': 'value'
                                        },
                                        ExpressionAttributeValues={
                                            ':v': {'N': value}
                                        }
                                    )

def get_user_details(user_id):
    user = db.get_item(TableName='users',
                    Key={'email': {'S': user_id}})
    if user.get('Item') == None:
        return None, None, None
    else:
        profile_picture = None
        first_name = user['Item']['first_name']['S']
        last_name = user['Item']['last_name']['S']
        user_name = first_name + ' ' + last_name
        home_community = user['Item']['home']['S']
        if user['Item'].get('profile_picture') != None:
            profile_picture = user['Item']['profile_picture']['S']
        return user_name, profile_picture, home_community


def check_if_user_liked(feed_id, user_id):
    liked = False
    user_like = db.get_item(TableName='likes',
                Key={'feed': {'S': feed_id},
                     'user': {'S': user_id}
                }
            )
    if user_like.get('Item') != None:
        liked = True
    return liked

def check_if_user_starred(feed_id, user_id):
    starred = False
    user_starred = db.query(TableName='stars_activity',
                IndexName='stars-activity-email-id',
                KeyConditionExpression='email = :e AND shared_id = :id',
                ExpressionAttributeValues={
                    ':e': {'S': user_id},
                    ':id': {'S': feed_id}
                }
            )
    if user_starred.get('Items') != []:
        starred = True
    return starred

def check_if_user_commented(feed_id, user_id):
    commented = False
    user_commented = db.query(TableName='comments',
                    IndexName='comments-feed-email',
                    KeyConditionExpression='feed_id = :id AND email = :e',
                    ExpressionAttributeValues={
                        ':id': {'S': feed_id},
                        ':e': {'S': user_id}
                    }
                )
    if user_commented.get('Items') != []:
        commented = True
    return commented

def get_challenge_state(id, key):
    challenge = db.get_item(TableName='challenges_activity',
                        Key={'email': {'S': id},
                             'accepted_time': {'S': key}
                        }
                    )
    challenge_state = challenge['Item']['state']['S']
    if challenge_state == 'COMPLETE':
        state = 'COMPLETE'
        return state
    elif challenge_state == 'INCOMPLETE':
        state = 'INCOMPLETE'
        return state
    elif challenge_state == 'ACTIVE':
        current_time = datetime.datetime.now()
        accepted_time = datetime.datetime.strptime(key, "%Y-%m-%d %H:%M:%S:%f")
        diff = current_time - accepted_time
        str_diff = str(diff).rsplit(' ', 2)
        if len(str_diff) > 1:
            if int(str_diff[0]) >= 2:
                change_state = db.update_item(TableName='challenges_activity',
                                    Key={'email': {'S': id},
                                         'accepted_time': {'S': key}
                                    },
                                    UpdateExpression='SET #s = :st',
                                    ExpressionAttributeNames={
                                        '#s': 'state'
                                    },
                                    ExpressionAttributeValues={
                                        ':st': {'S': 'INACTIVE'}
                                    }
                                )
                state = 'INACTIVE'
                return state
            else:
                state = 'ACTIVE'
                return state
        else:
            state = 'ACTIVE'
            return state
    elif challenge_state == 'INACTIVE':
        state = 'INACTIVE'
        return state

def check_if_taking_off(feed_id, feed):
    id = feed_id.rsplit('_', 1)[0]
    key = feed_id.rsplit('_', 1)[1]
    feed = db.get_item(TableName=feed,
                    Key={'email': {'S': id},
                         'creation_time': {'S': key}
                    }
                )
    value = feed['Item']['value']['N']
    if int(value) >= 50:
        taking_off = True
    else:
        taking_off = False
    return taking_off


def check_if_user_following_user(user1_id, user2_id):
    response = db.get_item(TableName='following_activity',
                            Key={'id1': {'S': user1_id},
                                 'id2': {'S': user2_id}
                            }
                        )

    following = False

    if response.get('Item') != None:
        if response['Item']['following']['S'] == 'True':
            following = True

    return following


def check_if_post_added_to_favorites(feed_id, user_id):
    added_to_fav = False
    fav = db.get_item(TableName='favorites',
                    Key={'email': {'S': user_id},
                         'feed_id': {'S': feed_id}
                    }
                )

    if fav.get('Item') != None:
        added_to_fav = True

    return added_to_fav


def check_if_challenge_accepted(challenge_id, user_id):
    challenge_accepted = False
    state = None
    accepted_time = None
    creator = challenge_id.rsplit('_', 1)[0]

    challenge = db.query(TableName='challenges_activity',
                    IndexName='challenge-id-email',
                    KeyConditionExpression='challenge_id = :c AND email = :e',
                    ExpressionAttributeValues={
                        ':c': {'S': challenge_id},
                        ':e': {'S': user_id}
                    }
                )

    if challenge.get('Items') != []:
        challenge_accepted = True
        accepted_time = challenge['Items'][0]['accepted_time']['S'] 
        state = get_challenge_state(user_id, accepted_time)

    return challenge_accepted, state, accepted_time


def get_challenge_accepted_users(challenge_id, user_id):
    creator = challenge_id.rsplit('_', 1)[0]

    users_list = db.query(TableName='challenges_activity', 
                      IndexName='challenge-id-email',
                      KeyConditionExpression='challenge_id = :c',
                      ExpressionAttributeValues={
                          ':c': {'S': challenge_id}
                      }
                  )
    accepted_users = []

    if users_list.get('Items') != []:
        for u in users_list['Items']:
            if creator != u['email']['S']:
                user_exists = check_if_user_exists(u['email']['S'])
                if user_exists:
                    user_name, profile_picture, home = get_user_details(
                                                        u['email']['S'])
                    following = check_if_user_following_user(user_id,
                                                        u['email']['S'])
                    user = {}
                    user['name'] = {}
                    user['id'] = u['email']
                    user['profile_picture'] = {}
                    user['home_community'] = {}
                    if user_id != u['email']['S']:
                        user['following'] = {}
                        user['following']['BOOL'] = following
                    user['name']['S'] = user_name
                    user['home_community']['S'] = home
                    user['profile_picture']['S'] = profile_picture
                    accepted_users.append(user)

    return accepted_users

def get_next_date(current_date):
    date_split = current_date.rsplit('-', 2)
    date = date_split[2]
    month = date_split[1]
    year = date_split[0]
    if int(date) > 1:
        next_date = int(date) - 1
        if 1 <= next_date <= 9:
            next_date = '0' + str(next_date)
        new_date = year + '-' + month + '-' + str(next_date)
    elif int(date) == 1:
        if int(month) > 1:
            new_month = int(month) - 1
            if 1 <= new_month <=9:
                new_month = '0' + str(new_month)
            new_date = year + '-' + str(new_month) \
                            + '-' + '31'
        if int(month) == 1:
            new_date = str(int(year) - 1) + '-' + '12' + '-' + '31'

    return new_date


def get_feeds(users, table, last_evaluated_key=None):
    today = str(datetime.date.today())

    feeds = []

    lek = None

    fetch = True

    while fetch:
        if last_evaluated_key != None:
            if last_evaluated_key.get('last_key') == None:
                date = get_next_date(last_evaluated_key['query_key'])
                # if table == 'posts':
                response = db.query(TableName=table,
                             Limit=100,
                             Select='ALL_ATTRIBUTES',
                             IndexName='creation-date-time',
                             KeyConditionExpression='creation_date = :d',
                             ExpressionAttributeValues={
                                 ':d': {'S': date}
                             },
                             ScanIndexForward=False
                         )
            else:
                date = last_evaluated_key['query_key']
                LastEvaluatedKey = last_evaluated_key['last_key']
                response = db.query(TableName=table,
                             Limit=100,
                             Select='ALL_ATTRIBUTES',
                             IndexName='creation-date-time',
                             KeyConditionExpression='creation_date = :d',
                             ExpressionAttributeValues={
                                 ':d': {'S': date}
                             },
                             ExclusiveStartKey=last_evaluated_key['last_key'],
                             ScanIndexForward=False
                         )
        else:
            date = today
            response = db.query(TableName=table,
                            Select='ALL_ATTRIBUTES',
                            Limit=100,
                            IndexName='creation-date-time',
                            KeyConditionExpression='creation_date = :d',
                            ExpressionAttributeValues={
                                ':d': {'S': date}
                            },
                            ScanIndexForward=False
                        )

        if response.get('Items') != []:
            for post in response['Items']:
                if post['email']['S'] in users:
                        feeds.append(post)
                        
        if response.get('LastEvaluatedKey') != None:
            last_evaluated_key = {}
            last_evaluated_key['last_key'] = response['LastEvaluatedKey']
            last_evaluated_key['query_key'] = date
        elif date == APP_DATE:
            last_evaluated_key = None
        else:
            last_evaluated_key= {}
            last_evaluated_key['query_key'] = date

        lek = last_evaluated_key

        if len(feeds) >= 50 or date == APP_DATE:
            fetch = False

    return feeds, lek


def update_notifications_activity_page(user_id, seen_activity):
    if seen_activity == False:
        update = db.put_item(TableName='notifications_activity_page',
                            Item={'email': {'S': user_id},
                                  'seen': {'BOOL': seen_activity}
                            }
                        )
    else:
        update = db.put_item(TableName='notifications_activity_page',
                            Item={'email': {'S': user_id},
                                  'seen': {'BOOL': seen_activity}
                            }
                        )
