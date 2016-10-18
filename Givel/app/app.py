from flask import Flask
from flask_mail import Mail

app = Flask('Givel')
mail = Mail(app)