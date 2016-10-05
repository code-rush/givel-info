import boto3
import datetime

from app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_posts_table
from app.helper import upload_post_file

from werkzeug.exceptions import BadRequest

user_post_activity_api_routes = Blueprint('post_activity_api', __name__)
api = Api(user_post_activity_api_routes)

BUCKET_NAME = 'givelposts'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'mpeg', 'mp4'])

db = boto3.client('dynamodb')
s3 = boto3.client('s3')

try: 
    try:
        table_response = db.describe_table(TableName='posts')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('Posts Table exists!')
    except:
        posts = create_posts_table()
        print('Posts Table created!')
except:
    pass


class UsersPost(Resource):
    def post(self, user_email):
        """Creates Post"""
        response = {}
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_id_ex = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        date = date_time.rsplit(' ', 1)[0]
        time = date_time.rsplit(' ', 1)[1]

        if request.form['content'] or ('file_count' in request.form and int(request.form['file_count'])) != 0:
            if int(request.form['file_count']) > 1:
                raise BadRequest('Only one file is allowed!')
            else:
                post = db.put_item(TableName='posts',
                                Item={'email': {'S': user_email},
                                     'creation_time': {'S': date_time},
                                     'date': {'S': date},
                                     'time': {'S': time},
                                     'value': {'N': '0'},
                                     'likes': {'N': '0'},
                                     'stars': {'N': '0'},
                                     'favorites': {'N': '0'},
                                     'comments': {'N': '0'}
                                }
                            )
                if 'location' in request.form:
                    post = db.update_item(TableName='posts',
                                          Key={'email':{'S': user_email},
                                               'creation_time': {'S': date_time}
                                          },
                                          UpdateExpression='SET #loc = :l',
                                          ExpressionAttributeNames={
                                              '#loc': 'location'
                                          },
                                          ExpressionAttributeValues={
                                              ':l': {'S': request.form['location']}
                                          }
                                      )
                else:
                    user = db.get_item(TableName='users',
                                    Key={'email': {'S': user_email}
                                    }
                                )
                    home_community = user['Item']['home']['S']
                    post = db.update_item(TableName='posts',
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
                if 'content' in request.form:
                    try:
                        post = db.update_item(TableName='posts',
                                              Key={'email': {'S': user_email},
                                                   'creation_time': {'S': date_time}
                                              },
                                              UpdateExpression='SET content = :d',
                                              ExpressionAttributeValues={
                                                  ':d': {'S': request.form['content']}
                                              }
                                          )
                        response['message'] = 'Success! Post Created!'
                    except:
                        post = db.delete_item(TableName='posts',
                                         Key={'email': {'S': user_email},
                                              'creation_time': {'S': date_time}
                                         }
                                     )
                        raise BadRequest('Failed to create post')
                if 'file_count' in request.form and int(request.form['file_count']) == 1:
                        f = request.files['file']
                        try:
                            media_file, file_type = upload_post_file(f, BUCKET_NAME,
                                             user_email+file_id_ex, ALLOWED_EXTENSIONS)
                            if file_type == 'picture_file':
                                post = db.update_item(TableName='posts',
                                                      Key={'email': {'S': user_email},
                                                           'creation_time': {'S': date_time}
                                                      },
                                                      UpdateExpression='ADD pictures :p',
                                                      ExpressionAttributeValues={
                                                          ':p': {'SS': [media_file]}
                                                      }
                                                  )
                            elif file_type == 'video_file':
                                post = db.update_item(TableName='posts',
                                                      Key={'email': {'S': user_email},
                                                           'creation_time': {'S': date_time}
                                                      },
                                                      UpdateExpression='ADD video :v',
                                                      ExpressionAttributeValues={
                                                          ':v': {'SS': [media_file]}
                                                      }
                                                  )
                            response['message'] = 'Success! Post Created!'
                        except:
                            post = db.delete_item(TableName='posts',
                                             Key={'email': {'S': user_email},
                                                  'creation_time': {'S': date_time}
                                             }
                                         )
                            raise BadRequest('Failed to create post')
                return response, 201


    def put(self):
        """Edit Post"""
        response = {}
        post_data = request.get_json(force=True)
        if post_data.get('id') == None or post_data.get('key') == None:
            raise BadRequest('Post ID and KEY is required to edit a post')
        if post_data.get('content') != None:
            try:
                post = db.update_item(TableName='posts',
                                    Key={'email': {'S': post_data['id']},
                                         'creation_time': {'S': post_data['key']}
                                    },
                                    UpdateExpression='SET content = :c',
                                    ExpressionAttributeValues={
                                        ':c': {'S': post_data['content']}
                                    }
                                )
                response['message'] = 'Successfully edited!'
            except:
                raise BadRequest('Failed to edit post!')
        else:
            raise BadRequest('Only post content is allowed to edit!')
        return response, 200


    def get(self, user_email):
        """Get all the user's posts"""
        response = {}
        try:
            user_posts = db.query(TableName='posts',
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
            for posts in user_posts['Items']:
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
                posts['id'] = {}
                posts['id']['S'] = posts['email']['S']
                posts['key'] = {}
                posts['key']['S'] = posts['creation_time']['S']
                del posts['email']
                del posts['creation_time']
                del posts['date']
                del posts['time']
            response['message'] = 'Successfully fetched users all posts!'
            response['result'] = user_posts['Items']
        except:
            response['message'] = 'Failed to fetch users posts!'
        return response, 200

    def delete(self):
        """Deletes User's Post"""
        response={}
        post_data = request.get_json(force=True)
        if post_data.get('id') == None or post_data.get('key') == None:
            raise BadRequest('Please provide required data')
        else:
            post = db.get_item(TableName='posts',
                               Key={'email': {'S': post_data['id']},
                                    'creation_time': {'S': post_data['key']}
                               }
                           )
            if post.get('pictures') != None:
                for picture in post['pictures']:
                    key = picture.rsplit('/', 1)[1]
                    delete_pic = s3.delete_object(Bucket=BUCKET_NAME, Key=key)
            if post.get('video') != None:
                for video in post['video']:
                    key = video.rsplit('/', 1)[1]
                    delete_video = s3.delete_object(Bucket=BUCKET_NAME, Key=key)

            delete_post = db.delete_item(TableName='posts',
                                        Key={'email': {'S': post_data['id']},
                                             'creation_time': {'S': post_data['key']}
                                        }
                                    )
            response['message'] = 'Post deleted!'
            return response, 200


class UserRepostFeed(Resource):
    def post(self, user_email):
        """Repost user's post"""
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = date_time.rsplit(' ', 1)[0]
        time = date_time.rsplit(' ', 1)[1]

        try:
            if data.get('id') == None or data.get('key') == None:
                raise BadRequest('Please provide post ID and Key!')
            else:
                post = db.get_item(TableName='posts',
                                Key={'email': {'S': data['id']},
                                     'creation_time': {'S': data['key']}
                                }
                            )
                repost = db.put_item(TableName='posts',
                            Item={'email': {'S': user_email},
                                 'creation_time': {'S': date_time},
                                 'date': {'S': date},
                                 'time': {'S': time},
                                 'value': {'N': '0'},
                                 'likes': {'N': '0'},
                                 'stars': {'N': '0'},
                                 'favorites': {'N': '0'},
                                 'comments': {'N': '0'}
                            }
                        )

                if post['Item'].get('content') != None:
                    repost = db.update_item(TableName='posts',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='SET content = :d',
                                      ExpressionAttributeValues={
                                          ':d': {'S': post['Item']['content']['S']}
                                      }
                                  )
                if post ['Item'].get('pictures') != None:
                    repost = db.update_item(TableName='posts',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='ADD pictures :p',
                                      ExpressionAttributeValues={
                                          ':p': {'SS': post['Item']['pictures']['SS']}
                                      }
                                  )
                if post['Item'].get('video') != None:
                    repost = db.update_item(TableName='posts',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='ADD video :v',
                                      ExpressionAttributeValues={
                                          ':v': {'SS': post['Item']['video']['SS']}
                                      }
                                  )
                if data.get('location') != None:
                    repost = db.update_item(TableName='posts',
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
                                    Key={'email': {'S': user_email}})
                    home_community = user['Item']['home']['S']
                    repost = db.update_item(TableName='posts',
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
                response['message'] = 'Repost successful!'
        except:
            response['message'] = 'Repost failed!'        
        return response, 200



api.add_resource(UsersPost, '/<user_email>/post',
                            '/posts')
api.add_resource(UserRepostFeed, '/<user_email>/post/repost')