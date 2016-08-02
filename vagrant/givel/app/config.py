from app.app import app

app.config['AWS_ACCESS_KEY_ID'] = aws_access_key_id
app.config['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key

# Testing on local database
app.config['DYNAMO_ENABLE_LOCAL'] = True
app.config['DYNAMO_LOCAL_HOST'] = 'localhost'
app.config['DYNAMO_LOCAL_PORT'] = 8888
