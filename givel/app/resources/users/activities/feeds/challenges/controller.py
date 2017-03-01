import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_challenges_table

from app.helper import (upload_post_file, check_challenge_state,
                        check_if_user_commented,
                        check_if_user_liked,
                        check_if_user_starred,
                        get_user_details, get_challenge_accepted_users,
                        check_if_taking_off, check_if_challenge_accepted,
                        check_if_user_following_user,
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


class UsersChallengePosts(Resource):
    def post(self, user_email):
        """Creates challenges"""
        response = {}
        challenge_data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        date = date_time.rsplit(' ', 1)[0]
        time = date_time.rsplit(' ', 1)[1]

        if challenge_data.get('description') == None:
            raise BadRequest('Cannot create an empty challenge!')
        else:
            user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}})

            challenge_post = db.put_item(TableName='challenges',
                            Item={'email': {'S': user_email},
                                  'creation_time': {'S': date_time},
                                  'creation_key': {'S': date_time},
                                  'likes': {'N': '0'},
                                  'value': {'N': '0'},
                                  'state': {'S': 'ACTIVE'},
                                  'comments': {'N': '0'},
                                  'stars': {'N': '0'},
                                  'description': {'S': 
                                          challenge_data['description']},
                                  'creator': {'S': user_email}
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
                response['message'] = 'Challenge edited successfully!'
            except:
                raise BadRequest('Failed to edit challenge!')
        elif challenge_data.get('state') != None:
            if challenge_data['state'] == 'inactive':
                try:
                    post = db.update_item(TableName='challenges',
                                        Key={'email': {'S': challenge_data['id']},
                                             'creation_time': {'S': challenge_data['key']}
                                        },
                                        UpdateExpression='SET #s = :st',
                                        ExpressionAttributeNames={
                                            '#s': 'state'
                                        },
                                        ExpressionAttributeValues={
                                            ':st': {'S': 'INACTIVE'}
                                        }
                                    )
                    response['message'] = 'Challenge edited successfully!'
                except:
                    raise BadRequest('Failed to edit challenge!')
            elif challenge_data['state'] == 'complete':
                try:
                    post = db.update_item(TableName='challenges',
                                        Key={'email': {'S': challenge_data['id']},
                                             'creation_time': {'S': challenge_data['key']}
                                        },
                                        UpdateExpression='SET #s = :st',
                                        ExpressionAttributeNames={
                                            '#s': 'state'
                                        },
                                        ExpressionAttributeValues={
                                            ':st': {'S': 'COMPLETE'}
                                        }
                                    )
                    response['message'] = 'Challenge edited successfully!'
                except:
                    raise BadRequest('Failed to edit challenge!')
            elif challenge_data['state'] == 'incomplete':
                try:
                    post = db.update_item(TableName='challenges',
                                        Key={'email': {'S': challenge_data['id']},
                                             'creation_time': {'S': challenge_data['key']}
                                        },
                                        UpdateExpression='SET #s = :st',
                                        ExpressionAttributeNames={
                                            '#s': 'state'
                                        },
                                        ExpressionAttributeValues={
                                            ':st': {'S': 'INCOMPLETE'}
                                        }
                                    )
                    response['message'] = 'Challenge edited successfully!'
                except:
                    raise BadRequest('Failed to edit challenge!')
            else:
                raise BadRequest('State can be either \'incomplete\' \
                                  or \'complete\' or \'inactive\'')
        else:
            raise BadRequest('Cannot post an empty challenge!')
        return response, 200

    def get(self, user_email):
        """Get all the user's challenges"""
        response = {}
        try:
            user_challenges = db.query(TableName='challenges',
                                Select='ALL_ATTRIBUTES',
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': user_email}
                                }
                            )
            for challenge in user_challenges['Items']:
                user_name, profile_picture, home = get_user_details(
                                                challenge['creator']['S'])
                if user_name == None:
                    del challenge
                else:
                    feed_id = challenge['creator']['S'] + '_' \
                              + challenge['creation_key']['S']
                    liked = check_if_user_liked(feed_id, user_email)
                    starred = check_if_user_starred(feed_id, user_email)
                    commented = check_if_user_commented(feed_id, user_email)
                    # state = check_challenge_state(user_email, \
                    #                      challenge['creation_time']['S'])
                    taking_off = check_if_taking_off(feed_id, 'challenges')
                    challenge_accepted, c_state = check_if_challenge_accepted(
                                                          feed_id, user_email)
                    accepted_users_list = get_challenge_accepted_users(
                                                    feed_id, user_email)
                    challenge['user'] = {}
                    challenge['user']['name'] = {}
                    challenge['user']['profile_picture'] = {}
                    challenge['user']['id'] = challenge['creator']
                    challenge['user']['name']['S'] = user_name
                    challenge['user']['profile_picture']['S'] = profile_picture
                    challenge['feed'] = {}
                    challenge['feed']['id'] = challenge['creator']
                    challenge['feed']['key'] = challenge['creation_key']
                    challenge['state'] = {}
                    challenge['state']['S'] = c_state
                    challenge['liked'] = {}
                    challenge['starred'] = {}
                    challenge['commented'] = {}
                    challenge['taking_off'] = {}
                    challenge['taking_off']['BOOL'] = taking_off
                    challenge['liked']['BOOL'] = liked
                    challenge['starred']['BOOL'] = starred
                    challenge['commented']['BOOL'] = commented
                    challenge['accepted'] = {}
                    challenge['accepted']['BOOL'] = challenge_accepted
                    challenge['accepted_users'] = {}
                    challenge['accepted_users']['SS'] = accepted_users_list 

                    if challenge['creator']['S'] != user_email:
                        following = check_if_user_following_user(user_email,
                                                challenge['creator']['S'])
                        challenge['user']['following'] = {}
                        challenge['user']['following']['BOOL'] = following
                    
                    del challenge['email']
                    del challenge['creator']
                    del challenge['value']
                    del challenge['creation_key']
            response['message'] = 'Successfully fetched users challenges!'
            response['result'] = user_challenges['Items']
        except:
            response['message'] = 'Failed to fetch users challenges!'
        return response, 200

    def delete(self, user_email):
        """Deletes User's Post"""
        response={}
        challenge_data = request.get_json(force=True)
        if challenge_data.get('id') == None or challenge_data.get('key') == None:
            raise BadRequest('Please provide required data')
        if challenge_data['id'] != str(user_email):
            raise BadRequest('Challenges can only be deleted by the creators!')
        else:
            try:
                delete_challenge = db.delete_item(TableName='challenges',
                                  Key={'email': {'S': challenge_data['id']},
                                       'creation_time': {'S': challenge_data['key']}
                                  }
                              )
                response['message'] = 'Challenge deleted!'
            except:
                response['message'] = 'Failed to delete Challenge. Try again later!'
            return response, 200


class AcceptChallenge(Resource):
    def put(self, user_email):
        """Accepts Challenge"""
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

        if data.get('id') == None and data.get('key') == None:
            raise BadRequest('Please provide ID and Key')
        else:
            user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}})

            try:
                challenge = db.get_item(TableName='challenges',
                                    Key={'email': {'S': data['id']},
                                         'creation_time': {'S': data['key']}
                                    }
                                )

                accept_challenge = db.put_item(TableName='challenges',
                        Item={'email': {'S': user_email},
                             'creation_time': {'S': date_time},
                             'creator': {'S': challenge['Item']\
                                                 ['creator']['S']},
                             'creation_key': {'S': challenge['Item']\
                                                 ['creation_key']['S']},
                             'likes': {'N': '0'},
                             'value': {'N': '0'},
                             'state': {'S': 'ACTIVE'},
                             'comments': {'N': '0'},
                             'stars': {'N': '0'},
                             'description': {'S': challenge['Item']\
                                                 ['description']['S']},
                             'only_to_followers': 
                                 {'BOOL': user['Item']\
                                         ['post_only_to_followers']['BOOL']},
                             'location': {'S': challenge['Item']\
                                                     ['location']['S']}
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

        if data.get('id') == None and data.get('key') == None:
            raise BadRequest('Please provide ID and Key')
        else:
            user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}})
            try:
                challenge = db.get_item(TableName='challenges',
                                    Key={'email': {'S': data['id']},
                                         'creation_time': {'S': data['key']}
                                    }
                                )

                post_challenge = db.put_item(TableName='challenges',
                                Item={'email': {'S': user_email},
                                     'creation_time': {'S': date_time},
                                     'creation_key': {'S': date_time},
                                     'creator': {'S': user_email},
                                     'likes': {'N': '0'},
                                     'value': {'N': '0'},
                                     'state': {'S': 'ACTIVE'},
                                     'comments': {'N': '0'},
                                     'stars': {'N': '0'},
                                     'description': {'S': challenge['Item']\
                                                     ['description']['S']},
                                     'only_to_followers': 
                                         {'BOOL': user['Item']\
                                          ['post_only_to_followers']['BOOL']}
                                }
                            )
                response['message'] = 'Challenge Posted as Own!'
            except:
                response['message'] = 'Try again later'
                return response, 400

            try:
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
                response['message'] = 'Challenge successfully created!'
                return response, 201
            except:
                rollback_feed = db.delete_item(TableName='challenges',
                                          Key={'email': {'S': user_email},
                                               'creation_time': {'S': date_time}
                                          }
                                      )
                response['message'] = 'Please try again later!'
                return response, 400
            return response, 201


class UsersChallengeRepost(Resource):
    def post(self, user_email):
        """Reposts user's challenge"""
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

        try:
            if data.get('id') == None and data.get('key') == None:
                raise BadRequest('Please provide ID and Key')
            else:
                user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}})

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
                                  'creation_key': {'S': date_time},
                                  'likes': {'N': '0'},
                                  'value': {'N': '0'},
                                  'state': {'S': 'ACTIVE'},
                                  'comments': {'N': '0'},
                                  'stars': {'N': '0'},
                                  'creator': {'S': user_email},
                                  'only_to_followers': 
                                      {'BOOL': user['Item']\
                                          ['post_only_to_followers']['BOOL']}
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
                    user = db.get_item(TableName='users',
                                    Key={'email': {'S': user_email}
                                    }
                                )
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
            response['message'] = 'Repost failed!'
        return response, 200


api.add_resource(UsersChallengePosts, '/<user_email>')
api.add_resource(UsersChallengeRepost, '/repost/<user_email>')
api.add_resource(PostChallengeAsOwn, '/post/<user_email>')
api.add_resource(AcceptChallenge, '/accept/<user_email>')
