import boto3
import datetime

from werkzeug.utils import secure_filename

s3 = boto3.client('s3')
db = boto3.client('dynamodb')

IMAGE = set(['jpg', 'png', 'jpeg'])
VIDEO = set(['mp4', 'mpeg'])
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
    communities = db.scan(TableName='communities')
    comm = community.rsplit(' ', 1)
    state = comm[1]
    city = comm[0][:-1]
    exist = False
    for i in communities['Items']:
        if i['state']['S'] == STATES[state] and i['city']['S'] == city:
            exist = True
            return city, state, exist
    return city, state, exist


def update_member_counts(city, state, operation):
    """Updates Member Counts"""
    if operation == 'add':
        update_count = db.update_item(TableName='communities',
                                    Key={'state': {'S': STATES[state]},
                                         'city': {'S': city},
                                    },
                                    UpdateExpression='SET members = members + :m',
                                    ExpressionAttributeValues={
                                        ':m': {'N': '1'}
                                    }
                                )
    elif operation == 'remove':
        update_count = db.update_item(TableName='communities',
                                    Key={'state': {'S': STATES[state]},
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
        feed_type = None
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
        return None, None
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

def check_challenge_state(id, key):
    challenge = db.get_item(TableName='challenges',
                        Key={'email': {'S': id},
                             'creation_time': {'S': key}
                        }
                    )
    if challenge['Item']['state']['S'] == 'COMPLETE':
        state = 'COMPLETE'
        return state
    elif challenge['Item']['state']['S'] == 'INCOMPLETE':
        state = 'INCOMPLETE'
        return state
    elif challenge['Item']['state']['S'] == 'ACTIVE':
        current_time = datetime.datetime.now()
        creation_time = datetime.datetime.strptime(key, "%Y-%m-%d %H:%M:%S")
        diff = current_time - creation_time
        str_diff = str(diff).rsplit(' ', 2)
        if len(str_diff) > 1:
            if int(str_diff[0]) >= 2:
                change_state = db.update_item(TableName='challenges',
                                    Key={'email': {'S': id},
                                         'creation_time': {'S': key}
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
    elif challenge['Item']['state']['S'] == 'INACTIVE':
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
    user1 = db.get_item(TableName='users',
               Key={'email': {'S': user1_id}})

    following = False
    if user1['Item'].get('following') != None:
        for user in user1['Item']['following']['SS']:
            if user == user2_id:
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
    c_id = challenge_id.rsplit('_',1)[0]

    if c_id == user_id:
        challenge_accepted = True

    return challenge_accepted

