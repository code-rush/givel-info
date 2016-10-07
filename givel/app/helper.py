import boto3
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


def update_likes(id, key, operation):
    if operation == 'like':
        update_count = db.update_item(TableName='posts',
                                Key={'email': {'S': id},
                                     'creation_time': {'S': key}
                                },
                                UpdateExpression='SET likes = likes + :l',
                                ExpressionAttributeValues={
                                    ':l': {'N': '1'}
                                }
                            )
    elif operation == 'unlike':
        update_count = db.update_item(TableName='posts',
                                Key={'email': {'S': id},
                                     'creation_time': {'S': key}
                                },
                                UpdateExpression='SET likes = likes - :l',
                                ExpressionAttributeValues={
                                    ':l': {'N': '1'}
                                }
                            )


def update_value(id, key, operation, stars=None):
    if operation == 'like':
        update_count = db.update_item(TableName='posts',
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
        update_count = db.update_item(TableName='posts',
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
            update_count = db.update_item(TableName='posts',
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

