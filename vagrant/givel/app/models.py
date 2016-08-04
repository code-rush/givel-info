import datetime
import boto3

dynamodb = boto3.resource('dynamodb')

def create_users_table():
    try:
        users_table = dynamodb.create_table(
           TableName='users',
           KeySchema=[
               {
                   'AttributeName': 'email',
                   'KeyType': 'HASH',
               }
           ],
           AttributeDefinitions=[
               {
                   'AttributeName': 'email',
                   'AttributeType': 'S'
               }
           ],
           ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
           }
        )
    except Exception as e:
        try:
            users_table = dynamodb.Table('users')
        except:
            print('Users Table does not exist.')
    finally:
        return users_table


# from pynamodb.models import Model
# from pynamodb.attributes import UnicodeAttribute, UnicodeSetAttribute
# from pynamodb.attributes import NumberAttribute
# from pynamodb.attributes import UTCDateTimeAttribute
# from pynamodb.attributes import JSONAttribute


# class Users(Model):
#    """User Profile"""
#    class Meta:
#        table_name = 'users'
#        read_capacity_units = 10
#        write_capacity_units = 10
#    email = UnicodeAttribute(hash_key=True)
#    first_name = UnicodeAttribute()
#    last_name = UnicodeAttribute()
#    password = UnicodeAttribute()
#    user_follwing = UnicodeSetAttribute(null=True)
#    user_followers = UnicodeSetAttribute(null=True)
#    communities = UnicodeSetAttribute(null=True)
#    primary_community = UnicodeAttribute(null=True)
#    profile_picture = UnicodeAttribute(null=True)
#    givel_stars = NumberAttribute(default=0)


# class Posts(Model):
#    """Posts Model"""
#    class Meta:
#        table_name = 'posts'
#        read_capacity_units = 1000
#        write_capacity_units = 10
#    description = UnicodeAttribute(null=True)
#    created_time = UTCDateTimeAttribute(default=datetime.datetime.now())
#    user = UnicodeAttribute()
#    hearts = NumberAttribute(default=0)
#    image = UnicodeAttribute(null=True)
#    video = UnicodeAttribute(null=True)
#    stars_achieved = NumberAttribute(default=0)


# class Communities(Model):
#    """Community Model"""
#    class Meta:
#        table_name = 'communities'
#        read_capacity_units = 10
#        write_capacity_units = 10
#    community_name = UnicodeAttribute(hash_key=True)
#    community_users = UnicodeSetAttribute()