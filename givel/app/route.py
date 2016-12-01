from app.home.controller import hw_bp
from app.resources.users.accounts.controller import user_account_api_routes
from app.resources.communities.controller import community_api_routes
from app.resources.users.activities.following.controller import user_following_activity_api_routes
from app.resources.users.activities.feeds.posts.controller import user_post_activity_api_routes
from app.resources.users.activities.feeds.challenges.controller import user_challenge_activity_api_routes
from app.resources.users.activities.feeds.controller import feed_activity_api_routes
from app.resources.reports.controller import report_activity_api_routes
from app.resources.organizations.controller import organizations_api_routes
from app.resources.organizations.uplift.controller import organizations_uplift_api_routes
from app.resources.search.controller import search_api_routes

def build_route(app):
    app.register_blueprint(hw_bp)
    app.register_blueprint(user_account_api_routes, url_prefix='/api/v1/users/accounts')
    app.register_blueprint(community_api_routes, url_prefix='/api/v1/communities')
    app.register_blueprint(user_following_activity_api_routes, url_prefix='/api/v1/users')
    app.register_blueprint(user_post_activity_api_routes, url_prefix='/api/v1/users/posts')
    app.register_blueprint(user_challenge_activity_api_routes, url_prefix='/api/v1/users/challenges')
    app.register_blueprint(feed_activity_api_routes, url_prefix='/api/v1/feeds')
    app.register_blueprint(report_activity_api_routes, url_prefix='/api/v1/reports')
    app.register_blueprint(organizations_api_routes, url_prefix='/api/v1/organizations')
    app.register_blueprint(organizations_uplift_api_routes, url_prefix='/api/v1/organizations/uplift')
    app.register_blueprint(search_api_routes, url_prefix='/api/v1/search')