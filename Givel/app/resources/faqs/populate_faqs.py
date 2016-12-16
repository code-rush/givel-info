import boto3

db = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')

try:
    qanda_table = dynamodb.create_table(
         TableName='QAs',
         KeySchema=[
             {
                 'AttributeName': 'q_no',
                 'KeyType': 'HASH'
             }
         ],
         AttributeDefinitions=[
             {
                 'AttributeName': 'q_no',
                 'AttributeType': 'S'
             }
         ],
         ProvisionedThroughput={
             'ReadCapacityUnits': 10,
             'WriteCapacityUnits': 10
         }
    )

    qanda_table.client.get_waiter('table_exists').wait(TableName='QAs')

    print(qanda_table.item_count)

except:
    pass


q1 = 'What is a community?'
a1 = 'When a new user signs up on Givel, they are prompted to choose one or '\
    +'two of the 50 communities shown. Although communities are listed via '\
    +'their city name, Givel elected to call cities “communities” since the '\
    +'word community describes much more than a physical location. '\
    +'Communities are important because they give users an opportunity to '\
    +'see even more positive content and provide an opportunity to easily '\
    +'connect with others outside of their circles. Communities are also '\
    +'important because they act as content monitors for user posts. You’ll '\
    +'notice this when you post a story, thought, photo, or challenge, as '\
    +'both your followers and communities will see what you posted.'

q2 = 'What are stars and how do they work?'
a2 = 'Think of stars as a type of social currency that can be collected or '\
    +'given away to others. They’re super unique because they can be used '\
    +'to show appreciation beyond a typical social response, such as a like '\
    +'(heart) or comment. They’re also valuable because they can be given '\
    +'to other members who post great content or do good deeds, or can be '\
    +'given to organizations on Uplift. When an organization receives stars '\
    +'on Uplift, each star turns the organization’s “billboard” into a free '\
    +'impression (view) on the Community Feed. This is fantastic for an '\
    +'organization’s reach, as well as for those who support these awesome '\
    +'organizations in their social or environmental movements.'

q3 = 'What are Challenges?'
a3 = 'Challenges are calls to action that motivate others to participate in '\
    +'various acts of kindness. They can be simple or a bit more challenging, '\
    +'depending on what the user has in mind when they create them. Once a '\
    +'challenge is activated, it begins a count down from 48 hours until '\
    +'either the timer runs out or an action has been taken. Challenges are '\
    +'always validated based on the honor system but you’re more than '\
    +'welcome to share a photo or video of your kind acts to inspire others!'

q4 = 'Can I change the time to complete a challenge?'
a4 = 'At this time the countdown for challenges can’t be changed. '\
    +'Thanks for asking though!'

q5 = 'What is Uplift and how does it work?'
a5 = 'Uplift is a place where users can discover some of the best social '\
    +'good and non profit organizations around. Uplift is especially unique '\
    +'because each time an organization earns a star on Uplift, the '\
    +'organization’s billboard is given a free impression (view) on the '\
    +'Community Feed. Givel created Uplift so users can differentiate '\
    +'between those organizations making a positive societal or environmental '\
    +'impact and those simply out to make a profit. Organizations love Uplift '\
    +'because they can grow their audience and increase their impact through '\
    +'greater visibility.'

q6 = 'What’s the difference between a social good organization and a '\
    +'non profit on Givel?'
a6 = 'Non profits on Givel are vetted through Charity Navigator, where they '\
    +'are given a rating based on a variety of factors, including the '\
    +'percent of total expenses spent on the cause they support. Social good '\
    +'organizations also provide great impact, yet they are for profit '\
    +'companies. Like non profits, social good organizations on Givel have '\
    +'been certified through bcorporation.net, where they are given '\
    +'an “Overall B Score”.'

q7 = 'How do I add my organization on Givel?'
a7 = 'In order for an organization to make its way onto Givel, it must have '\
    +'been vetted through Charity Navigator or certified as a B Corporation. '\
    +'While Givel would love to have your organization listed on Uplift, '\
    +'please note that we do not currently add charities that fall within '\
    +'the following categories– a) Hospitals and Hospital Foundations, b) '\
    +'Land Trusts, c) Universities, Colleges, Private Schools, and '\
    +'School-based Foundations, d) Sorority and Fraternity Foundations, '\
    +'e) Community Foundations and Donor Advised Funds, and f) Religious '\
    +'Organizations. Thanks for your interest!'



question1 = db.put_item(TableName='QAs',
                Item={'q_no': {'S': '1'},
                      'question': {'S': q1},
                      'answer': {'S': a1}
                }
            )

question2 = db.put_item(TableName='QAs',
                Item={'q_no': {'S': '2'},
                      'question': {'S': q2},
                      'answer': {'S': a2}
                }
            )

question3 = db.put_item(TableName='QAs',
                Item={'q_no': {'S': '3'},
                      'question': {'S': q3},
                      'answer': {'S': a3}
                }
            )

question4 = db.put_item(TableName='QAs',
                Item={'q_no': {'S': '4'},
                      'question': {'S': q4},
                      'answer': {'S': a4}
                }
            )

question5 = db.put_item(TableName='QAs',
                Item={'q_no': {'S': '5'},
                      'question': {'S': q5},
                      'answer': {'S': a5}
                }
            )

question6 = db.put_item(TableName='QAs',
                Item={'q_no': {'S': '6'},
                      'question': {'S': q6},
                      'answer': {'S': a6}
                }
            )

question7 = db.put_item(TableName='QAs',
                Item={'q_no': {'S': '7'},
                      'question': {'S': q7},
                      'answer': {'S': a7}
                }
            )

print('FAQs added!')

