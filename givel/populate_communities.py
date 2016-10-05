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
                    'AttributeName': 'state',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'city',
                    'KeyType': 'RANGE'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    communities_table.client.get_waiter('table_exists').wait(TableName='communities')

    print(communities_table.item_count)

except:
    pass




community1 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'New York'},
                               'state': {'S': 'New York'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community2 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Los Angeles'},
                               'state': {'S': 'California'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community3 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Chicago'},
                               'state': {'S': 'Illinois'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community4 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Houston'},
                               'state': {'S': 'Texas'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community5 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Philadelphia'},
                               'state': {'S': 'Pennsylvania'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community6 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Phoenix'},
                               'state': {'S': 'Arizona'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community7 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'San Antonio'},
                               'state': {'S': 'Texas'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community8 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'San Diego'},
                               'state': {'S': 'California'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community9 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Dallas'},
                               'state': {'S': 'Texas'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community10 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'San Jose'},
                               'state': {'S': 'California'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community11 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Austin'},
                               'state': {'S': 'Texas'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community12 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Jacksonville'},
                               'state': {'S': 'Florida'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community13 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'San Francisco'},
                               'state': {'S': 'California'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community14 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Indianapolis'},
                               'state': {'S': 'Indiana'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community15 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Columbus'},
                               'state': {'S': 'Ohio'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community16 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Fort Worth'},
                               'state': {'S': 'Texas'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community17 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Charlotte'},
                               'state': {'S': 'North Carolina'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community18 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Detroit'},
                               'state': {'S': 'Michigan'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community19 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'El Paso'},
                               'state': {'S': 'Texas'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community20 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Seattle'},
                               'state': {'S': 'Washington'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community21 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Denver'},
                               'state': {'S': 'Colorado'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community22 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Washington'},
                               'state': {'S': 'DC'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community23 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Memphis'},
                               'state': {'S': 'Tennessee'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community24 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Boston'},
                               'state': {'S': 'Massachusetts'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community25 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Nashville-Davidson'},
                               'state': {'S': 'Tennessee'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community26 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Baltimore'},
                               'state': {'S': 'Maryland'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community27 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Oklahoma'},
                               'state': {'S': 'Oklahoma'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community28 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Portland'},
                               'state': {'S': 'Oregon'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community29 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Las Vegas'},
                               'state': {'S': 'Nevada'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community30 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Louisville-Jefferson County'},
                               'state': {'S': 'Kentucky'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community31 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Milwaukee'},
                               'state': {'S': 'Wisconsin'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community32 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Albuquerque'},
                               'state': {'S': 'New Mexico'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community33 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Tucson'},
                               'state': {'S': 'Arizona'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community34 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Fresno'},
                               'state': {'S': 'California'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community35 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Sacramento'},
                               'state': {'S': 'California'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community36 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Long Beach'},
                               'state': {'S': 'California'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community37 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Kansas City'},
                               'state': {'S': 'Missouri'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community38 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Mesa'},
                               'state': {'S': 'Arizona'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community39 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Atlanta'},
                               'state': {'S': 'Georgia'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community40 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Virginia Beach'},
                               'state': {'S': 'Virginia'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community41 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Omaha'},
                               'state': {'S': 'Nebraska'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community42 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Colorado Springs'},
                               'state': {'S': 'Colorado'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community43 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Raleigh'},
                               'state': {'S': 'North Carolina'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community44 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Miami'},
                               'state': {'S': 'Florida'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community45 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Oakland'},
                               'state': {'S': 'California'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community46 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Minneapolis'},
                               'state': {'S': 'Minnesota'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community47 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Tulsa'},
                               'state': {'S': 'Oklahoma'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community48 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Cleveland'},
                               'state': {'S': 'Ohio'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community49 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Wichita'},
                               'state': {'S': 'Kansas'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community50 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'New Orleans'},
                               'state': {'S': 'Louisiana'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

community51 = db.put_item(TableName='communities',
                         Item={'city': {'S': 'Arlington'},
                               'state': {'S': 'Texas'},
                               'members': {'N': '0'}
                         },
                         ConditionExpression='attribute_not_exists(city)',
                     )

print('Communities added!')