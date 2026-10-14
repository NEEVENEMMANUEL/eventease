"""EventEase application factory."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import get_config

db = SQLAlchemy()


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    db.init_app(app)

    from app import metrics
    metrics.init_app(app)

    from app.routes import bp
    app.register_blueprint(bp)

    # Make build info available to every template (footer version banner).
    @app.context_processor
    def inject_build_info():
        return {
            "build_number": app.config["BUILD_NUMBER"],
            "git_sha": app.config["GIT_SHA"],
        }

    with app.app_context():
        db.create_all()

    return app
