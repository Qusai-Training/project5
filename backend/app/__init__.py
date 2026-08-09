import os

from flask import Flask, send_from_directory, redirect
from flask_cors import CORS

from app.config import Config

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
JS_DIR = os.path.join(FRONTEND_DIR, "js")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    CORS(app)

    from app.errors import register_error_handlers
    register_error_handlers(app)

    from app.routes.auth_routes import auth_bp
    from app.routes.course_routes import course_bp
    from app.routes.skill_routes import skill_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(user_bp)

    @app.route("/static/<path:filename>")
    def serve_static(filename):
        return send_from_directory(STATIC_DIR, filename)

    @app.route("/js/<path:filename>")
    def serve_js(filename):
        return send_from_directory(JS_DIR, filename)

    @app.route("/<page>.html")
    def serve_page(page):
        return send_from_directory(TEMPLATES_DIR, f"{page}.html")

    @app.route("/")
    def index():
        return redirect("/login.html")

    return app


app = create_app()
