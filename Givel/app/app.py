from flask import Flask
from flask_mail import Mail

app = Flask('Givel')
app.secret_key = 'DEV_SECRET_KEY'
mail = Mail(app)