import boto3

db = boto3.client('dynamodb')

try:
    communities_table = db.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'city',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'state',
                    'AttributeType': 'S'
                }
            ],
            TableName='communities',
            KeySchema=[
                {
                    'AttributeName': 'city',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'state',
                    'KeyType': 'RANGE'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'ReadCapacityUnits': 10
            }
        )
except:
    pass



community1 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'New York'},
                               'state': {'S': 'New York'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community2 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Los Angeles'},
                               'state': {'S': 'California'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community3 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Chicago'},
                               'state': {'S': 'Illinois'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community4 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Houston'},
                               'state': {'S': 'Texas'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community5 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Philadelphia'},
                               'state': {'S': 'Pennsylvania'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community6 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Phoenix'},
                               'state': {'S': 'Arizona'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community7 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'San Antonio'},
                               'state': {'S': 'Texas'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community8 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'San Diego'},
                               'state': {'S': 'California'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community9 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Dallas'},
                               'state': {'S': 'Texas'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community10 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'San Jose'},
                               'state': {'S': 'California'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community11 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Austin'},
                               'state': {'S': 'Texas'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community12 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Jacksonville'},
                               'state': {'S': 'Florida'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community13 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'San Francisco'},
                               'state': {'S': 'California'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community14 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Indianapolis'},
                               'state': {'S': 'Indiana'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community15 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Columbus'},
                               'state': {'S': 'Ohio'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community16 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Fort Worth'},
                               'state': {'S': 'Texas'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community17 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Charlotte'},
                               'state': {'S': 'North Carolina'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community18 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Detroit'},
                               'state': {'S': 'Michigan'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community19 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'El Paso'},
                               'state': {'S': 'Texas'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community20 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Seattle'},
                               'state': {'S': 'Washington'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community21 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Denver'},
                               'state': {'S': 'Colorado'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

# community22 = db.put_item(TableName='communities',
#                          Item={'city': {'S': 'Washington'},
#                                'state': {'S': 'DC'}
#                          },
#                          ConditionExpression='attribute_not_exists(city)',
#                      )

community23 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Memphis'},
                               'state': {'S': 'Tennessee'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community24 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Boston'},
                               'state': {'S': 'Massachusetts'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community25 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Nashville-Davidson'},
                               'state': {'S': 'Tennessee'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community26 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Baltimore'},
                               'state': {'S': 'Maryland'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community27 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Oklahoma'},
                               'state': {'S': 'Oklahoma'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community28 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Portland'},
                               'state': {'S': 'Oregon'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community29 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Las Vegas'},
                               'state': {'S': 'Nevada'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community30 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Louisville-Jefferson County'},
                               'state': {'S': 'Kentucky'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community31 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Milwaukee'},
                               'state': {'S': 'Wisconsin'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community32 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Albuquerque'},
                               'state': {'S': 'New Mexico'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community33 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Tucson'},
                               'state': {'S': 'Arizona'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community34 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Fresno'},
                               'state': {'S': 'California'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community35 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Sacramento'},
                               'state': {'S': 'California'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community36 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Long Beach'},
                               'state': {'S': 'California'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community37 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Kansas City'},
                               'state': {'S': 'Missouri'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community38 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Mesa'},
                               'state': {'S': 'Arizona'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community39 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Atlanta'},
                               'state': {'S': 'Georgia'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community40 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Virginia Beach'},
                               'state': {'S': 'Virginia'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community41 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Omaha'},
                               'state': {'S': 'Nebraska'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community42 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Colorado Springs'},
                               'state': {'S': 'Colorado'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community43 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Raleigh'},
                               'state': {'S': 'North Carolina'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community44 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Miami'},
                               'state': {'S': 'Florida'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community45 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Oakland'},
                               'state': {'S': 'California'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community46 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Minneapolis'},
                               'state': {'S': 'Minnesota'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community47 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Tulsa'},
                               'state': {'S': 'Oklahoma'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community48 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Cleveland'},
                               'state': {'S': 'Ohio'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community49 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Wichita'},
                               'state': {'S': 'Kansas'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community50 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'New Orleans'},
                               'state': {'S': 'Louisiana'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community51 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Arlington'},
                               'state': {'S': 'Texas'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )