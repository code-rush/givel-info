from app.app import app

app.config['AWS_ACCESS_KEY_ID'] = YOUR_ACCESS_KEY
app.config['AWS_SECRET_ACCESS_KEY'] = YOUR_SECRET_ACCESS_KEY

# Testing on local database
app.config['DYNAMO_ENABLE_LOCAL'] = True
app.config['DYNAMO_LOCAL_HOST'] = 'localhost'
app.config['DYNAMO_LOCAL_PORT'] = 8000
