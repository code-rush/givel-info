import datetime

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UnicodeSetAttribute
from pynamodb.attributes import NumberAttribute
from pynamodb.attributes import UTCDateTimeAttribute


class Users(Model):
   """User Profile"""
   class Meta:
       table_name = 'users'
       read_capacity_units = 10
       write_capacity_units = 10
   email = UnicodeAttribute(hash_key=True)
   first_name = UnicodeAttribute()
   last_name = UnicodeAttribute()
   password = UnicodeAttribute()
   user_follwing = UnicodeSetAttribute(null=True)
   user_followers = UnicodeSetAttribute(null=True)
   communities = UnicodeSetAttribute(null=True)
   primary_community = UnicodeAttribute()
   profile_picture = UnicodeAttribute(null=True)
   givel_stars = NumberAttribute(default=0)


class Posts(Model):
   """Posts Model"""
   class Meta:
       table_name = 'posts'
       read_capacity_units = 1000
       write_capacity_units = 10
   description = UnicodeAttribute(null=True)
   created_time = UTCDateTimeAttribute(default=datetime.now)
   user = UnicodeAttribute()
   hearts = NumberAttribute(default=0)
   image = UnicodeAttribute(null=True)
   video = UnicodeAttribute(null=True)
   stars_achieved = NumberAttribute(default=0)


class Communities(Model):
   """Community Model"""
   class Meta:
       table_name = 'communities'
       read_capacity_units = 10
       write_capacity_units = 10
   community_name = UnicodeAttribute(hash_key=True)
   community_users = UnicodeSetAttribute()