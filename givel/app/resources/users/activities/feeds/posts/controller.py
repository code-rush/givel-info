import boto3
import datetime

from app.app import app

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import (create_posts_table,
                        create_favorite_posts_table)

from app.helper import (upload_post_file, check_if_user_exists,
                        check_if_user_liked, check_if_taking_off,
                        check_if_user_starred, check_if_user_commented,
                        get_user_details, check_if_post_added_to_favorites,
                        check_if_user_following_user)


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
        data = request.get_json(force=True)

        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

        if data.get('content') == None:
            raise BadRequest('Post cannot be empty. Please provide '\
                                            + 'content of the post.')
        if data.get('file_count') == None:
            raise BadRequest('Please provide file_count. If no files are ' \
                                              + 'sent, set file_count to 0')
        if int(data['file_count']) != 0 and int(data['file_count']) > 1:
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
                
                if data.get('location') != None:
                    post = db.update_item(TableName='posts',
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
                
                if data.get('content') != None:
                    post = db.update_item(TableName='posts',
                                  Key={'email': {'S': user_email},
                                       'creation_time': {'S': date_time}
                                  },
                                  UpdateExpression='SET content = :d',
                                  ExpressionAttributeValues={
                                      ':d': {'S': data['content']}
                                  }
                              )

                if data.get('tags') != None:
                    tags = []
                    for t in data['tags']:
                        tag_entry = {}
                        tag_entry['M'] = {}
                        tag_entry['M']['user_id'] = {}
                        tag_entry['M']['user_id']['S'] = t['user_id']
                        tag_entry['M']['origin'] = {}
                        tag_entry['M']['origin']['N'] = str(t['origin'])
                        tag_entry['M']['length'] = {}
                        tag_entry['M']['length']['N'] = str(t['length'])
                        tags.append(tag_entry)

                    post = db.update_item(TableName='posts',
                                Key={'email': {'S': user_email},
                                     'creation_time': {'S': date_time}
                                },
                                UpdateExpression='SET tags = :t',
                                ExpressionAttributeValues={
                                    ':t': {'L': tags}
                                }
                            )

                    feed_id = str(user_email) + '_' + date_time

                    for i in tags:
                        tag_notification = db.put_item(TableName='notifications',
                                Item={'notify_to': {'S': i['M']['user_id']['S']},
                                      'creation_time': {'S': date_time},
                                      'email': {'S': user_email},
                                      'from': {'S': 'feed'},
                                      'feed_id': {'S': feed_id},
                                      'checked': {'BOOL': False},
                                      'notify_for': {'S': 'tagging'},
                                      'tagged_where': {'S': 'post'}
                                }
                            )
                if int(data['file_count']) > 0:
                    response['feed'] = {}
                    response['feed']['id'] = {}
                    response['feed']['key'] = {}
                    response['feed']['id']['S'] = user_email
                    response['feed']['key']['S'] = date_time

                response['message'] = 'Success! Post Created!'
            except:
                post = db.delete_item(TableName='posts',
                             Key={'email': {'S': user_email},
                                  'creation_time': {'S': date_time}
                             }
                         )
                response['message'] = 'Failed to create post. Try again later.'
            return response, 201


    def put(self, user_email):
        """Edit Post"""
        response = {}

        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

        post_data = request.get_json(force=True)
        if post_data.get('id') == None or post_data.get('key') == None:
            raise BadRequest('Post ID and KEY is required to edit a post')
        if post_data['id'] != str(user_email):
            raise BadRequest('Posts can only be edited by the creators!')
        try:
            feed_id = post_data['id'] + '_' + post_data['key']
            if post_data.get('content') != None:
                post = db.update_item(TableName='posts',
                                    Key={'email': {'S': post_data['id']},
                                         'creation_time': {'S': post_data['key']}
                                    },
                                    UpdateExpression='SET content = :c',
                                    ExpressionAttributeValues={
                                        ':c': {'S': post_data['content']}
                                    }
                                )

                if post_data.get('tags') != None:
                    resp = db.get_item(TableName='posts', 
                            Key={'email': {'S': post_data['id']},
                                 'creation_time': {'S': post_data['key']}
                            }
                        )
                    tags = []
                    for t in post_data['tags']:
                        tag_entry = {}
                        tag_entry['M'] = {}
                        tag_entry['M']['user_id'] = {}
                        tag_entry['M']['user_id']['S'] = t['user_id']
                        tag_entry['M']['origin'] = {}
                        tag_entry['M']['origin']['N'] = str(t['origin'])
                        tag_entry['M']['length'] = {}
                        tag_entry['M']['length']['N'] = str(t['length'])
                        tags.append(tag_entry)

                    post = db.update_item(TableName='posts',
                                Key={'email': {'S': user_email},
                                     'creation_time': {'S': post_data['key']}
                                },
                                UpdateExpression='SET tags = :t',
                                ExpressionAttributeValues={
                                    ':t': {'L': tags}
                                }
                            )
                    for i in tags:
                        if resp['Item'].get('tags') == None:
                            tag_notification = db.put_item(
                                    TableName='notifications',
                                    Item={'notify_to': 
                                              {'S': i['M']['user_id']['S']},
                                          'creation_time': {'S': date_time},
                                          'email': {'S': user_email},
                                          'from': {'S': 'feed'},
                                          'feed_id': {'S': feed_id},
                                          'checked': {'BOOL': False},
                                          'notify_for': {'S': 'tagging'},
                                          'tagged_where': {'S': 'post'}
                                    }
                                )
                        elif resp['Item'].get('tags') != None \
                          and i not in resp['Item']['tags']['L']:
                            tag_notification = db.put_item(
                                    TableName='notifications',
                                    Item={'notify_to': 
                                              {'S': i['M']['user_id']['S']},
                                          'creation_time': {'S': date_time},
                                          'email': {'S': user_email},
                                          'from': {'S': 'feed'},
                                          'feed_id': {'S': feed_id},
                                          'checked': {'BOOL': False},
                                          'notify_for': {'S': 'tagging'},
                                          'tagged_where': {'S': 'post'}
                                    }
                                )

            if post_data.get('file') != None:
                if post_data['file'] == 'remove':
                    if post['Item'].get('pictures') != None:
                        for picture in post['Item']['pictures']['SS']:
                            key = picture.rsplit('/', 1)[1]
                            s3.delete_object(Bucket=BUCKET_NAME, Key=key)

                        post = db.update_item(TableName='posts',
                                Key={'email': {'S': post_data['id']},
                                     'creation_time': {'S': post_data['key']}
                                },
                                UpdateExpression='REMOVE pictures'
                            )
                    if post['Item'].get('videos') != None:
                        for video in post['Item']['videos']['SS']:
                            key = video.rsplit('/', 1)[1]
                            s3.delete_object(Bucket=BUCKET_NAME, Key=key)

                        post = db.update_item(TableName='posts',
                                Key={'email': {'S': post_data['id']},
                                     'creation_time': {'S': post_data['key']}
                                },
                                UpdateExpression='REMOVE videos'
                            )
            response['message'] = 'Successfully edited!'
        except:
            raise BadRequest('edit post request failed! Try again later.')
        return response, 200


    def get(self, user_email):
        """Get all the user's posts"""
        response = {}
        try:
            user_posts = db.query(TableName='posts',
                                Select='ALL_ATTRIBUTES',
                                Limit=50,
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
                    added_to_fav = check_if_post_added_to_favorites(feed_id, 
                                                                  user_email)
                    posts['user'] = {}
                    posts['user']['name'] = {}
                    posts['user']['id'] = {}
                    posts['user']['profile_picture'] = {}
                    posts['user']['id']['S'] = user_email
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
                    posts['added_to_fav'] = {}
                    posts['added_to_fav']['BOOL'] = added_to_fav

                    if posts.get('tags') != None:
                        tags = []
                        for t in posts['tags']['L']:
                            tags.append(t['M'])
                        posts['tags']['L'] = tags

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


class FileActivityOnPost(Resource):
    def put(self, user_email):
        response = {}

        file_id_ex = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

        if request.form.get('id') == None or request.form.get('key') == None:
            raise BadRequest('Please provide feed id and key!')
        if request.form.get('file_count') == None:
            raise BadRequest('Please provide file_count. If no files are ' \
                                              + 'sent, set file_count to 0')
        if int(request.form['file_count']) != 0 and int(request.form['file_count']) > 1:
            raise BadRequest('Only one file is allowed!')
        elif request.form['id'] != user_email:
            raise BadRequest('Only the creator of the post is allowed to edit the post.')
        else:
            old_post = db.get_item(TableName='posts', 
                        Key={'email': {'S': request.form['id']},
                             'creation_time': {'S': request.form['key']}
                        }
                    )
            try:
                if 'file_count' in request.form and int(request.form['file_count']) == 1:
                    f = request.files['file']
                    media_file, file_type = upload_post_file(f, BUCKET_NAME,
                                     user_email+file_id_ex, ALLOWED_EXTENSIONS)
                    if file_type == 'picture_file':
                        post = db.update_item(TableName='posts',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': request.form['key']}
                                      },
                                      UpdateExpression='ADD pictures :p',
                                      ExpressionAttributeValues={
                                          ':p': {'SS': [media_file]}
                                      }
                                  )
                    elif file_type == 'video_file':
                        post = db.update_item(TableName='posts',
                                      Key={'email': {'S': user_email},
                                           'creation_time': {'S': request.form['key']}
                                      },
                                      UpdateExpression='ADD videos :v',
                                      ExpressionAttributeValues={
                                          ':v': {'SS': [media_file]}
                                      }
                                  )
                response['message'] = 'Successfully added picture to post!'
            except:
                raise BadRequest('Request failed! Try again later.')

            return response,200
                


class UserRepostFeed(Resource):
    def post(self, user_email):
        """Repost user's post"""
        response = {}
        data = request.get_json(force=True)
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

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
        """Add post to user's favorites"""
        response = {}
        data = request.get_json(force=True)

        if data.get('id') == None or data.get('key') == None:
            raise BadRequest('Provide feed id and key to add to the favorites')
        else:
            user_exists = check_if_user_exists(user_email)
            feed_id = str(data['id']) + '_' + str(data['key'])
            try:
                if user_exists == True:
                    add_to_fav = db.put_item(TableName='favorites',
                                    Item={'email': {'S': user_email},
                                          'feed_id': {'S': feed_id}
                                    }
                                )
                    response['message'] = 'Post added to your favorites'
                else:
                    raise BadRequest('User does not exist! ' \
                                   + 'Sign Up to add post to favorites')
            except:
                response['message'] = 'Try again later'
            return response, 200

    def delete(self, user_email):
        """Delete post from user's favorites"""
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
        """Gets user's favorite posts"""
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
            response['result'] = favorites
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
                    
                    if p.get('Item') != None:
                        user_name, profile_picture, home = get_user_details(p_id)
                        liked = check_if_user_liked(feed['feed_id']['S'], user_email)
                        starred = check_if_user_starred(feed['feed_id']['S'], user_email)
                        commented = check_if_user_commented(feed['feed_id']['S'], user_email)
                        taking_off = check_if_taking_off(feed['feed_id']['S'], 'posts')
                        added_to_fav = check_if_post_added_to_favorites(
                                            feed['feed_id']['S'], user_email)
                        post = p['Item']
                        post['user'] = {}
                        post['user']['id'] = p_id
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
                        post['added_to_fav'] = {}
                        post['added_to_fav']['BOOL'] = added_to_fav

                        if p_id != user_email:
                            following = check_if_user_following_user(
                                                     p_id, user_email)
                            post['user']['following'] = {}
                            post['user']['following']['BOOL'] = following

                        del post['email']
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
api.add_resource(FileActivityOnPost, '/files/<user_email>')

