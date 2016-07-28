from app.home.controller import hw_bp

def build_route(app):
   app.register_blueprint(hw_bp)