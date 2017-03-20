import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import (create_challenges_table, 
                        create_challenges_activity_table)

from app.helper import (upload_post_file, check_if_user_commented,
                        check_if_user_liked, check_if_user_starred,
                        get_user_details, get_challenge_accepted_users,
                        check_if_taking_off, check_if_challenge_accepted,
                        check_if_user_following_user, check_if_user_exists,
                        update_notifications_activity_page)

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
            print('challenges Table exists!')
    except:
        challenges = create_challenges_table()
        print('challenges Table created!')
except:
    pass

try:
    try:
        table_response = db.describe_table(TableName='challenges_activity')
        if table_response['Table']['TableStatus']:
            print('challenges_activity Table exists!')
    except:
        challenges_activity = create_challenges_activity_table()
        print('challenges_activity Table created!')
except:
    pass


class UsersChallengePosts(Resource):
    def post(self, user_email):
        """Creates challenges"""
        response = {}
        challenge_data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d")
        date = date_time.rsplit(' ', 1)[0]
        time = date_time.rsplit(' ', 1)[1]

        if challenge_data.get('description') == None:
            raise BadRequest('Cannot create an empty challenge!')

        user = db.get_item(TableName='users',
                            Key={'email': {'S': user_email}})

        challenge_id = str(user_email) + '_' + date_time
        challenge_post = db.put_item(TableName='challenges',
                        Item={'email': {'S': user_email},
                              'creation_time': {'S': date_time},
                              'likes': {'N': '0'},
                              'value': {'N': '0'},
                              'comments': {'N': '0'},
                              'stars': {'N': '0'},
                              'description': {'S': 
                                      challenge_data['description']},
                              'creation_date': {'S': creation_date}
                        }
                    )

        add_activity = db.put_item(TableName='challenges_activity',
                        Item={'email': {'S': user_email},
                              'accepted_time': {'S': date_time},
                              'challenge_id': {'S': challenge_id},
                              'state': {'S': 'ACTIVE'}
                        }
                    )
        try:
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
                                      ':l': {'S': 
                                          challenge_data['location']}
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
        except:
            rollback_feed = db.delete_item(TableName='challenges',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      }
                                  )
            raise BadRequest('Request Failed! Please try again later!')

    def put(self, user_email):
        """Edit Challenge"""
        response = {}
        challenge_data = request.get_json(force=True)

        if challenge_data.get('id') == None or challenge_data.get('key') == None:
            raise BadRequest('Challenge ID and KEY is required to edit a feed')
        if challenge_data['id'] != str(user_email):
            raise BadRequest('Challenges can only be edited by the creators!')
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
                response['message'] = 'Request successful. Challenge edited.'
            except:
                response['message'] = 'Failed to edit challenge.'

        return response, 200

    def delete(self, user_email):
        """Deletes User's Post"""
        response={}
        challenge_data = request.get_json(force=True)

        if challenge_data.get('id') == None or challenge_data.get('key') == None:
            raise BadRequest('Please provide required data')
        if challenge_data['id'] != str(user_email):
            raise BadRequest('Challenges can only be deleted by the creators!')

        try:
            delete_challenge = db.delete_item(TableName='challenges',
                              Key={'email': {'S': challenge_data['id']},
                                   'creation_time': {'S': challenge_data['key']}
                              }
                          )
            delete_activity = db.delete_item(TableName='challenges_activity', 
                              Key={'email': {'S': challenge_data['id']},
                                   'accepted_time': {'S': challenge_data['key']}
                              }
                          )
            response['message'] = 'Challenge deleted!'
        except:
            response['message'] = 'Failed to delete Challenge. Try again later!'
        return response, 200


class GetUsersChallenges(Resource):
    def post(self):
        """Get all the user's challenges"""
        response = {}
        data = request.get_json(force=True)

        if data.get('user_id') == None:
            raise BadRequest('Please provide user_id.')

        user_exists = check_if_user_exists(data['user_id'])

        if not user_exists:
            raise BadRequest('User does not exist.')

        if data.get('last_evaluated_key') == None:
            user_challenges = db.query(TableName='challenges_activity',
                                Limit=50,
                                Select='ALL_ATTRIBUTES',
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': data['user_id']}
                                },
                                ScanIndexForward=False
                            )
        else:
            user_challenges = db.query(TableName='challenges_activity',
                                Limit=50,
                                Select='ALL_ATTRIBUTES',
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': data['user_id']}
                                },
                                ExclusiveStartKey=data['last_evaluated_key'],
                                ScanIndexForward=False
                            )

        if user_challenges.get('LastEvaluatedKey') != None:
            response['last_evaluated_key'] = user_challenges['LastEvaluatedKey']

        feeds = []

        try:
            for challenges in user_challenges['Items']:
                c_id = challenges['challenge_id']['S'].rsplit('_', 1)[0]
                c_key = challenges['challenge_id']['S'].rsplit('_', 1)[1]

                challenge = db.get_item(TableName='challenges',
                                        Key={'email': {'S': c_id},
                                             'creation_time': {'S': c_key}
                                        }
                                    )

                user_name, profile_picture, home = get_user_details(
                                                challenge['Item']['email']['S'])
                if user_name == None:
                    pass
                else:
                    feed_id = challenges['challenge_id']['S']
                    liked = check_if_user_liked(feed_id, data['user_id'])
                    starred = check_if_user_starred(feed_id, data['user_id'])
                    commented = check_if_user_commented(feed_id, 
                                                        data['user_id'])
                    taking_off = check_if_taking_off(feed_id, 'challenges')
                    accepted, state, ac_time = check_if_challenge_accepted(
                                                  feed_id, data['user_id'])
                    accepted_users_list = get_challenge_accepted_users(
                                                    feed_id, data['user_id'])

                    challenge['Item']['user'] = {}
                    challenge['Item']['user']['name'] = {}
                    challenge['Item']['user']['profile_picture'] = {}
                    challenge['Item']['user']['id'] = challenge['Item']['email']
                    challenge['Item']['user']['name']['S'] = user_name
                    challenge['Item']['user']['profile_picture']['S'] = profile_picture
                    challenge['Item']['feed'] = {}
                    challenge['Item']['feed']['id'] = challenge['Item']['email']
                    challenge['Item']['feed']['key'] = challenge['Item']['creation_time']
                    challenge['Item']['state'] = {}
                    challenge['Item']['state']['S'] = state
                    challenge['Item']['liked'] = {}
                    challenge['Item']['starred'] = {}
                    challenge['Item']['commented'] = {}
                    challenge['Item']['taking_off'] = {}
                    challenge['Item']['taking_off']['BOOL'] = taking_off
                    challenge['Item']['liked']['BOOL'] = liked
                    challenge['Item']['starred']['BOOL'] = starred
                    challenge['Item']['commented']['BOOL'] = commented
                    challenge['Item']['accepted'] = {}
                    challenge['Item']['accepted']['BOOL'] = accepted
                    challenge['Item']['accepted_users'] = {}
                    challenge['Item']['accepted_users']['SS'] = accepted_users_list
                    challenge['Item']['accepted_time'] = {}
                    challenge['Item']['accepted_time']['S'] = ac_time

                    if challenge['Item']['email']['S'] != data['user_id']:
                        following = check_if_user_following_user(data['user_id'],
                                                challenge['Item']['email']['S'])
                        challenge['Item']['user']['following'] = {}
                        challenge['Item']['user']['following']['BOOL'] = following

                    del challenge['Item']['email']
                    del challenge['Item']['value']
                    del challenge['Item']['creation_date']

                    feeds.append(challenge['Item'])

            response['message'] = 'Request successful.'
            response['result'] = feeds
        except:
            response['message'] = 'Request failed. Try again later.'

        return response, 200


class ChangeChallengeState(Resource):
    def put(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest("Please provide challenge's id and key.")
        if data.get('accepted') == None or data.get('state') == None:
            raise BadRequest("Please provide challenge's " \
                             + "accepted and state values.")
        if data.get('new_state') == None:
            raise BadRequest("Please provide new_state to change the "\
                           + "challenge's state to.")
        if data['accepted'] == False:
            raise BadRequest("Accept the challenge first inorder to " \
                             + "change the state.")
        if data['state'] == 'COMPLETE' or data['state'] == 'INCOMPLETE':
            raise BadRequest("Challenge's state can only be changed if the "\
                         + "current state is 'ACTIVE' or 'INACTIVE'.")

        if data['new_state'].upper() == 'INACTIVE' \
          or data['new_state'].upper() == 'COMPLETE' \
          or data['new_state'].upper() == 'INCOMPLETE':
            challenge_id = data['id'] + '_' + data['key']
            challenge = db.query(TableName='challenges_activity',
                            IndexName='challenge-id-email',
                            KeyConditionExpression='challenge_id = :c \
                                                    AND email = :e',
                            ExpressionAttributeValues={
                                ':c': {'S': challenge_id},
                                ':e': {'S': user_email}
                            }
                        )
            if challenge.get('Items') != []:
                activity_key = challenge['Items'][0]['accepted_time']['S']
                update = db.update_item(TableName='challenges_activity',
                                Key={'email': {'S': user_email},
                                     'accepted_time': {'S': activity_key}
                                },
                                UpdateExpression='SET #s = :st',
                                ExpressionAttributeNames={
                                    '#s': 'state'
                                },
                                ExpressionAttributeValues={
                                    ':st': {'S': data['new_state'].upper()}
                                }
                            )

            response['message'] = 'Request successful. State changed.'
            return response, 200
        else:
            raise BadRequest("State can be either 'incomplete', " \
                            + "'complete' or 'inactive'.")


class AcceptChallenge(Resource):
    def put(self, user_email):
        """Accepts Challenge"""
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d")

        if data.get('id') == None and data.get('key') == None:
            raise BadRequest('Please provide ID and Key')

        user = db.get_item(TableName='users',
                            Key={'email': {'S': user_email}})

        try:
            challenge_id = data['id'] + '_' + data['key']
            accept_challenge = db.put_item(TableName='challenges_activity',
                                    Item={'email': {'S': user_email},
                                          'accepted_time': {'S': date_time},
                                          'challenge_id': {'S': challenge_id},
                                          'state': {'S': 'ACTIVE'}
                                    }
                                )

            if data['id'] != user_email:
                notification = db.put_item(TableName='notifications',
                                Item={'notify_to': {'S': data['id']},
                                      'creation_time': {'S': date_time},
                                      'email': {'S': user_email},
                                      'from': {'S': 'feed'},
                                      'feed_id': 
                                          {'S': str(data['id'])+'_'\
                                                +str(data['key'])},
                                      'checked': {'BOOL': False},
                                      'feed_type': {'S': 'challenges'},
                                      'notify_for': {'S': 
                                              'accepting challenge'}
                                }
                            )
                update_notifications_activity_page(data['id'], False)
            response['message'] = 'Challenge Accepted!'
        except:
            response['message'] = 'Try again later'
        return response, 200


class PostChallengeAsOwn(Resource):
    def post(self, user_email):
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d")

        if data.get('id') == None and data.get('key') == None:
            raise BadRequest('Please provide ID and Key')

        user = db.get_item(TableName='users',
                            Key={'email': {'S': user_email}})
        try:
            challenge_id = str(user_email) + '_' + date_time
            challenge = db.get_item(TableName='challenges',
                                Key={'email': {'S': data['id']},
                                     'creation_time': {'S': data['key']}
                                }
                            )

            post_challenge = db.put_item(TableName='challenges',
                            Item={'email': {'S': user_email},
                                 'creation_time': {'S': date_time},
                                 'likes': {'N': '0'},
                                 'value': {'N': '0'},
                                 'comments': {'N': '0'},
                                 'stars': {'N': '0'},
                                 'description': {'S': challenge['Item']\
                                                 ['description']['S']},
                                 'creation_date': {'S': creation_date}
                            }
                        )

            add_activity = db.put_item(TableName='challenges_activity',
                            Item={'email': {'S': user_email},
                                  'accepted_time': {'S': date_time},
                                  'challenge_id': {'S': challenge_id},
                                  'state': {'S': 'ACTIVE'}
                            }
                        )

            if data.get('location'):
                challenge_post = db.update_item(TableName='challenges',
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
            response['message'] = 'Challenge successfully created as own.'
        except:
            rollback_feed = db.delete_item(TableName='challenges',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      }
                                  )
            rollback_activity = db.delete_item(TableName='challenges_activity',
                                      Key={'email': {'S': user_email},
                                           'accepted_time': {'S': date_time}
                                      }
                                  )
            response['message'] = 'Request failed. Please try again later.'

        return response, 200


class UsersChallengeRepost(Resource):
    def post(self, user_email):
        """Reposts user's challenge"""
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d")

        if data.get('id') == None and data.get('key') == None:
            raise BadRequest('Please provide ID and Key')
        
        try:
            user = db.get_item(TableName='users',
                            Key={'email': {'S': user_email}})

            challenge_id = str(user_email) + '_' + date_time

            challenge = db.get_item(TableName='challenges',
                            Key={'email': {'S': data['id']},
                                 'creation_time': {'S': data['key']}
                            }
                        )

            repost_challenge = db.put_item(TableName='challenges',
                        Item={'email': {'S': user_email},
                              'creation_time': {'S': date_time},
                              'description': {'S': challenge['Item']\
                                                  ['description']['S']},
                              'likes': {'N': '0'},
                              'value': {'N': '0'},
                              'comments': {'N': '0'},
                              'stars': {'N': '0'},
                              'creation_date': {'S': creation_date}
                        }
                    )

            add_activity = db.put_item(TableName='challenges_activity',
                            Item={'email': {'S': user_email},
                                  'accepted_time': {'S': date_time},
                                  'challenge_id': {'S': challenge_id},
                                  'state': {'S': 'ACTIVE'}
                            }
                        )

            if data.get('location') != None:
                repost_challenge = db.update_item(TableName='challenges',
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
                repost_challenge = db.update_item(TableName='challenges',
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
            rollback_feed = db.delete_item(TableName='challenges',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      }
                                  )
            rollback_activity = db.delete_item(TableName='challenges_activity',
                                      Key={'email': {'S': user_email},
                                           'accepted_time': {'S': date_time}
                                      }
                                  )
            response['message'] = 'Repost failed!'

        return response, 200


api.add_resource(UsersChallengePosts, '/<user_email>')
api.add_resource(UsersChallengeRepost, '/repost/<user_email>')
api.add_resource(PostChallengeAsOwn, '/post/<user_email>')
api.add_resource(AcceptChallenge, '/accept/<user_email>')
api.add_resource(ChangeChallengeState, '/state/change/<user_email>')
api.add_resource(GetUsersChallenges, '/')
