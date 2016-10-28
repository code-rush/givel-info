import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import create_posts_table
from app.models import create_favorite_posts_table

from app.helper import upload_post_file
from app.helper import check_if_user_liked
from app.helper import check_if_user_starred
from app.helper import check_if_user_commented
from app.helper import get_user_details
from app.helper import check_if_taking_off

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

try: 
    try:
        table_response = db.describe_table(TableName='favorites')
        if table_response['Table']['TableStatus'] == 'ACTIVE':
            print('favorites Table exists!')
    except:
        favorites = create_favorite_posts_table()
        print('favorites Table created!')
except:
    pass


class UsersPost(Resource):
    def post(self, user_email):
        """Creates Post"""
        response = {}
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_id_ex = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        if request.form['content'] or ('file_count' in request.form and int(request.form['file_count'])) != 0:
            if int(request.form['file_count']) > 1:
                raise BadRequest('Only one file is allowed!')
            else:
                user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}})
                try:
                    post = db.put_item(TableName='posts',
                                    Item={'email': {'S': user_email},
                                         'creation_time': {'S': date_time},
                                         'value': {'N': '0'},
                                         'likes': {'N': '0'},
                                         'stars': {'N': '0'},
                                         'favorites': {'N': '0'},
                                         'comments': {'N': '0'},
                                         'only_to_followers': 
                                             {'BOOL': user['Item']['post_only_to_followers']['BOOL']}
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
                        post = db.update_item(TableName='posts',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='SET content = :d',
                                      ExpressionAttributeValues={
                                          ':d': {'S': request.form['content']}
                                      }
                                  )
                    if 'file_count' in request.form and int(request.form['file_count']) == 1:
                        f = request.files['file']
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
                                          UpdateExpression='ADD videos :v',
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


    def put(self, user_email):
        """Edit Post"""
        response = {}
        post_data = request.get_json(force=True)
        if post_data.get('id') == None or post_data.get('key') == None:
            raise BadRequest('Post ID and KEY is required to edit a post')
        if post_data['id'] != str(user_email):
            raise BadRequest('Posts can only be edited by the creators!')
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
                                # ConsistentRead=True,
                                KeyConditionExpression='email = :e',
                                ExpressionAttributeValues={
                                    ':e': {'S': user_email}
                                }
                            )
            for posts in user_posts['Items']:
                user_name, profile_picture, home = get_user_details(user_email)
                if user_name == None:
                    del posts
                else:
                    feed_id = posts['email']['S'] + '_' + posts['creation_time']['S']
                    liked = check_if_user_liked(feed_id, user_email)
                    starred = check_if_user_starred(feed_id, user_email)
                    commented = check_if_user_commented(feed_id, user_email)
                    taking_off = check_if_taking_off(feed_id, 'posts')
                    posts['user'] = {}
                    posts['user']['name'] = {}
                    posts['user']['profile_picture'] = {}
                    posts['user']['name']['S'] = user_name
                    posts['user']['profile_picture']['S'] = profile_picture
                    posts['feed'] = {}
                    posts['feed']['id'] = {}
                    posts['feed']['id']['S'] = posts['email']['S']
                    posts['feed']['key'] = {}
                    posts['feed']['key']['S'] = posts['creation_time']['S']
                    posts['liked'] = {}
                    posts['starred'] = {}
                    posts['commented'] = {}
                    posts['taking_off'] = {}
                    posts['taking_off']['BOOL'] = taking_off
                    posts['liked']['BOOL'] = liked
                    posts['starred']['BOOL'] = starred
                    posts['commented']['BOOL'] = commented
                    del posts['email']
                    del posts['value']
            response['message'] = 'Successfully fetched users all posts!'
            response['result'] = user_posts['Items']
        except:
            response['message'] = 'Failed to fetch users posts!'
        return response, 200

    def delete(self, user_email):
        """Deletes User's Post"""
        response={}
        post_data = request.get_json(force=True)
        if post_data.get('id') == None or post_data.get('key') == None:
            raise BadRequest('Please provide required data')
        if post_data['id'] != str(user_email):
            raise BadRequest('Posts can only be deleted by the creators!')
        else:
            post = db.get_item(TableName='posts',
                               Key={'email': {'S': post_data['id']},
                                    'creation_time': {'S': post_data['key']}
                               }
                           )
            if post['Item'].get('pictures') != None:
                for picture in post['Item']['pictures']['SS']:
                    key = picture.rsplit('/', 1)[1]
                    s3.delete_object(Bucket=BUCKET_NAME, Key=key)
            if post['Item'].get('videos') != None:
                for video in post['Item']['videos']['SS']:
                    key = video.rsplit('/', 1)[1]
                    s3.delete_object(Bucket=BUCKET_NAME, Key=key)

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

        try:
            if data.get('id') == None or data.get('key') == None:
                raise BadRequest('Please provide post ID and Key!')
            else:
                user = db.get_item(TableName='users',
                                Key={'email': {'S': user_email}})

                post = db.get_item(TableName='posts',
                                Key={'email': {'S': data['id']},
                                     'creation_time': {'S': data['key']}
                                }
                            )
                repost = db.put_item(TableName='posts',
                            Item={'email': {'S': user_email},
                                 'creation_time': {'S': date_time},
                                 'value': {'N': '0'},
                                 'likes': {'N': '0'},
                                 'stars': {'N': '0'},
                                 'favorites': {'N': '0'},
                                 'comments': {'N': '0'},
                                 'only_to_followers': 
                                     {'BOOL': user['Item']['post_only_to_followers']['BOOL']}
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
                if post['Item'].get('videos') != None:
                    repost = db.update_item(TableName='posts',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': date_time}
                                      },
                                      UpdateExpression='ADD videos :v',
                                      ExpressionAttributeValues={
                                          ':v': {'SS': post['Item']['videos']['SS']}
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


class UsersFavoritePosts(Resource):
    def put(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('Provide feed id and key to add to the favorites')
        else:
            feed_id = str(data['id']) + '_' + str(data['key'])
            try:
                add_to_fav = db.put_item(TableName='favorites',
                                Item={'email': {'S': user_email},
                                      'feed_id': {'S': feed_id}
                                }
                            )
                response['message'] = 'Post added to your favorites'
            except:
                response['message'] = 'Try again later'
            return response, 200

    def delete(self, user_email):
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('Provide feed id and key to delete post')
        else:
            feed_id = str(data['id']) + '_' + str(data['key'])
            try:
                delete_fav = db.delete_item(TableName='favorites',
                                Key={'email': {'S': user_email},
                                     'feed_id': {'S': feed_id}
                                }
                            )
                response['message'] = 'Post deleted from your favorites'
            except:
                response['message'] = 'Try again later'
            return response, 200

    def get(self, user_email):
        response = {}
        favorites = []
        favorite_posts = db.query(TableName='favorites',
                        Select='ALL_ATTRIBUTES',
                        KeyConditionExpression='email = :e',
                        ExpressionAttributeValues={
                            ':e': {'S': user_email}
                        }
                    )

        if favorite_posts.get('Items') == []:
            response['message'] = 'You have no favorite posts!'
        else:
            try:
                for feed in favorite_posts['Items']:
                    p_id = feed['feed_id']['S'].rsplit('_',1)[0]
                    p_key = feed['feed_id']['S'].rsplit('_',1)[1]
                    p = db.get_item(TableName='posts',
                            Key={'email': {'S': p_id},
                                 'creation_time': {'S': p_key}
                            }
                        )
                    user_name, profile_picture, home = get_user_details(p_id)
                    liked = check_if_user_liked(feed['feed_id']['S'], user_email)
                    starred = check_if_user_starred(feed['feed_id']['S'], user_email)
                    commented = check_if_user_commented(feed['feed_id']['S'], user_email)
                    taking_off = check_if_taking_off(feed['feed_id']['S'], 'posts')
                    post = p['Item']
                    post['user'] = {}
                    post['user']['name'] = {}
                    post['user']['profile_picture'] = {}
                    post['user']['name']['S'] = user_name
                    post['user']['profile_picture']['S'] = profile_picture
                    post['feed'] = {}
                    post['feed']['id'] = p['Item']['email']
                    post['feed']['key'] = p['Item']['creation_time']
                    post['liked'] = {}
                    post['starred'] = {}
                    post['commented'] = {}
                    post['taking_off'] = {}
                    post['taking_off']['BOOL'] = taking_off
                    post['liked']['BOOL'] = liked
                    post['starred']['BOOL'] = starred
                    post['commented']['BOOL'] = commented
                    del post['email']
                    del post['creation_time']
                    del post['value']
                    favorites.append(post)
                response['message'] = 'Successfully fetched all favorites'
                response['result'] = favorites
            except:
                response['message'] = 'Request Failed! Try again later'

        return response, 200




api.add_resource(UsersPost, '/<user_email>')
api.add_resource(UserRepostFeed, '/repost/<user_email>')
api.add_resource(UsersFavoritePosts, '/favorites/<user_email>')

