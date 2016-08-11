import boto3

from flask import Blueprint, request, json
from flask_restful import Resource, Api

from app.models import create_community_table

dynamodb = boto3.resource('dynamodb')

try:
    communities = create_community_table()
    print('Communities table is being created')
finally:
    communities = dynamodb.Table('communitites')
    print('Connected to communities')


COMMUNITIES = ['Albuquerque', 'Atlanta', 'Austin', 'Baltimore',
               'Boston', 'Charlotte', 'Chicago', 'Cleveland', 'Columbus', 
               'Colorado Springs', 'Dallas', 'Denver', 'Detroit', 'El Paso', 
               'Fort Worth', 'Fresno', 'Houston', 'Indianapolis', 
               'Jacksonville', 'Kansas City', 'Las Vegas', 'Long Beach', 
               'Los Angeles', 'Louisville-Jefferson County', 'Mesa', 'Memphis',
               'Miami', 'Milwaukee', 'Minneapolis', 'Nashville-Davidson', 
               'New Orleans', 'New York', 'Oakland', 'Oklahoma', 'Omaha', 
               'Philadelphia', 'Phoenix', 'Portland', 'Raleigh', 'Sacramento',
               'San Antonio', 'San Diego', 'San Francisco', 'San Jose', 
               'Seattle', 'Tuscon', 'Tulsa', 'Virginia', 'Washington', 
               'Wichita']

