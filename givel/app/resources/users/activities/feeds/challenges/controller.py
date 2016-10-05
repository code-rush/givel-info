import boto3
import datetime

from app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_challenges_table
from app.models import create_posts_table
from app.helper import upload_post_file

from werkzeug.exceptions import BadRequest

user_challenge_activity_api_routes = Blueprint('challenge_activity_api', __name__)
api = Api(user_challenge_activity_api_routes)

BUCKET_NAME = 'givelposts'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'mpeg', 'mp4'])

db = boto3.client('dynamodb')
s3 = boto3.client('s3')


try:
    try:
        table_response = db.describe_table(TableName='challenges')
        if table_response['Table']['TableStatus']:
            print('Challenges Table exists!')
    except:
        challenges = create_challenges_table()
        print('Challenges Table created!')
except:
    pass


class UsersChallengePosts(Resource):
    def post(self, user_email):
        """Creates challenges"""
        response = {}
        challenge_data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = date_time.rsplit(' ', 1)[0]
        time = date_time.rsplit(' ', 1)[1]

        if challenge_data.get('description') == None:
            raise BadRequest('Cannot create an empty challenge!')
        else:
            challenge_post = db.put_item(TableName='challenges',
                                    Item={'email': {'S': user_email},
                                          'creation_time': {'S': date_time},
                                          'likes': {'N': '0'},
                                          'value': {'N': '0'},
                                          'status': {'S': 'ACTIVE'},
                                          'comments': {'N': '0'},
                                          'favorites': {'N': '0'},
                                          'date': {'S': date},
                                          'time': {'S': time},
                                          'stars': {'N': '0'},
                                          'description': {'S': challenge_data['description']}
                                    }
                                )
            if challenge_data.get('location'):
                challenge_post = db.update_item(TableName='challenges',
                                      Key={'email':{'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='SET #loc = :l',
                                      ExpressionAttributeNames={
                                              '#loc': 'location'
                                          },
                                      ExpressionAttributeValues={
                                          ':l': {'S': challenge_data['location']}
                                      }
                                  )
            else:
                user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}
                                }
                            )
                home_community = user['Item']['home']['S']
                challenge_post = db.update_item(TableName='challenges',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='SET #loc = :l',
                                      ExpressionAttributeNames={
                                          '#loc': 'location'
                                      },
                                      ExpressionAttributeValues={
                                          ':l': {'S': home_community}
                                      }
                                  )
            response['message'] = 'Challenge successfully created!'
            return response, 201

    def put(self):
        """Edit Challenge"""
        response = {}
        challenge_data = request.get_json(force=True)
        if challenge_data.get('id') == None or challenge_data.get('key') == None:
            raise BadRequest('Challenge ID and KEY is required to edit a post')
        if challenge_data.get('description') != None:
            try:
                post = db.update_item(TableName='challenges',
                                    Key={'email': {'S': challenge_data['id']},
                                         'creation_time': {'S': challenge_data['key']}
                                    },
                                    UpdateExpression='SET description = :c',
                                    ExpressionAttributeValues={
                                        ':c': {'S': challenge_data['description']}
                                    }
                                )
                response['message'] = 'Successfully edited!'
            except:
                raise BadRequest('Failed to edit challenge!')
        else:
            raise BadRequest('Only challenge description is allowed to edit!')
        return response, 200

    def get(self, user_email):
        """Get all the user's challenges"""
        response = {}
        try:
            user_challenges = db.query(TableName='challenges',
                                Select='ALL_ATTRIBUTES',
                                Limit=50,
                                ConsistentRead=True,
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': user_email}
                                }
                            )
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').rsplit(' ', 1)
            current_date = current_datetime[0].rsplit('-',2)
            current_time = current_datetime[1].rsplit(':',2)
            for posts in user_challenges['Items']:
                post_date = posts['date']['S'].rsplit('-',2)
                post_time = posts['time']['S'].rsplit(':',2)
                if post_date[0] == current_date[0]:
                    if post_date[1] == current_date[1]:
                        if post_date[2] == current_date[2]:
                            if post_time[0] == current_time[0]:
                                if post_time[1] == current_time[1]:
                                    if post_time[2] == current_time[2]:
                                        posted_time = '0s'
                                    else:
                                        posted_time = str(int(current_time[2]) - int(post_time[2])) + 's'
                                else:
                                    posted_time = str(int(current_time[1]) - int(post_time[1])) + 'm'
                            else:
                                posted_time = str(int(current_time[0]) - int(post_time[0])) + 'hr'
                        else:
                            pt = int(current_date[2]) - int(post_date[2])
                            if pt == 1:
                                posted_time = 'yesterday'
                            else:
                                posted_time = str(pt) + 'd'
                    else:
                        posted_time = str(int(current_date[1]) - int(post_date[1])) + 'M'
                else:
                    posted_time = str(int(current_date[0]) - int(post_date[0])) + 'yr'
                # post_time = calculate_post_deltatime(posts['date'])
                posts['posted_time'] = {}
                posts['posted_time']['S'] = posted_time
                del posts['date']
                del posts['time']
            response['message'] = 'Successfully fetched users all challenges!'
            response['result'] = user_challenges['Items']
        except:
            response['message'] = 'Failed to fetch users posts!'
        return response, 200

    def delete(self):
        """Deletes User's Post"""
        response={}
        challenge_data = request.get_json(force=True)
        if challenge_data.get('id') == None or challenge_data.get('key') == None:
            raise BadRequest('Please provide required data')
        else:
            delete_challenge = db.delete_item(TableName='challenges',
                               Key={'email': {'S': challenge_data['id']},
                                    'creation_time': {'S': challenge_data['key']}
                               }
                           )

            response['message'] = 'Challenge deleted!'
            return response, 200


class UsersChallengeRepost(Resource):
    def post(self, user_email):
        """Reposts user's challenge"""
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = date_time.rsplit(' ', 1)[0]
        time = date_time.rsplit(' ', 1)[1]

        try:
            if data.get('id') == None and data.get('key') == None:
                raise BadRequest('Please provide ID and Key')
            else:
                post = db.get_item(TableName='challenges',
                                Key={'email': {'S': data['id']},
                                     'creation_time': {'S': data['key']}
                                }
                            )
                repost = db.put_item(TableName='challenges',
                                        Item={'email': {'S': user_email},
                                              'creation_time': {'S': date_time},
                                              'description': {'S': post['Item']['description']['S']},
                                              'likes': {'N': '0'},
                                              'value': {'N': '0'},
                                              'status': {'S': 'ACTIVE'},
                                              'comments': {'N': '0'},
                                              'favorites': {'N': '0'},
                                              'date': {'S': date},
                                              'time': {'S': time},
                                              'stars': {'N': '0'}
                                        }
                                    )
                if data.get('location') != None:
                    repost = db.update_item(TableName='challenges',
                                          Key={'email':{'S': user_email},
                                               'creation_time': {'S': date_time}
                                          },
                                          UpdateExpression='SET #loc = :l',
                                          ExpressionAttributeNames={
                                              '#loc': 'location'
                                          },
                                          ExpressionAttributeValues={
                                              ':l': {'S': data['location']}
                                          }
                                      )
                else:
                    user = db.get_item(TableName='users',
                                    Key={'email': {'S': user_email}
                                    }
                                )
                    repost = db.update_item(TableName='challenges',
                                          Key={'email': {'S': user_email},
                                               'creation_time': {'S': date_time}
                                          },
                                          UpdateExpression='SET #loc = :l',
                                          ExpressionAttributeNames={
                                              '#loc': 'location'
                                          },
                                          ExpressionAttributeValues={
                                              ':l': {'S': user['Item']['home']['S']}
                                          }
                                      )
                response['message'] = 'Repost successful!'
        except:
            response['media_file'] = 'Repost failed!'
        return response, 200


api.add_resource(UsersChallengePosts, '/<user_email>/challenge', 
                                 '/challenges')
api.add_resource(UsersChallengeRepost, '/<user_email>/challenge/repost')