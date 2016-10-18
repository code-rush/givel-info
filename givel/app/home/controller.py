from flask import Blueprint
from flask_restful import Resource, Api
from app.app import app

hw_bp = Blueprint('home', __name__)
api = Api(hw_bp)

class HelloWorld(Resource):
   def get(self):
       return {'Hello': 'HelloWorld'}

api.add_resource(HelloWorld, '/')