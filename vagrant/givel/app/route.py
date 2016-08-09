from app.home.controller import hw_bp
from app.resources.user_accounts.controller import user_account_api_routes
from app.resources.user_activities.controller import user_acitivity_api_routes


def build_route(app):
   app.register_blueprint(hw_bp)
   app.register_blueprint(user_account_api_routes, url_prefix='/api/v1/user_accounts')
   app.register_blueprint(user_activity_api_routes, url_prefix='/api/v1/users')