from flask import Flask
from flask_cors import CORS
from app.errors import register_error_handlers
from app.routes.auth_routes import auth_bp
from app.routes.course_routes import course_bp
from app.routes.skill_routes import skill_bp

def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="")
    CORS(app)

    # Register Error Handlers
    register_error_handlers(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(skill_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)