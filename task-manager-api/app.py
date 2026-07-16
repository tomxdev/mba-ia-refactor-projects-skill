"""Composition root — app factory: config, extensões, blueprints e error handler."""
import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from utils.helpers import now_utc


def create_app():
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    app.config.from_object(Settings)

    CORS(app)
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.route("/health")
    def health():
        return {"status": "ok", "timestamp": str(now_utc())}

    @app.route("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    register_error_handlers(app)

    with app.app_context():
        # Importa os models para que create_all reconheça as tabelas.
        from models import Category, Task, User  # noqa: F401

        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=Settings.DEBUG, host=Settings.HOST, port=Settings.PORT)
