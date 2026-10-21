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

    # NOTE: table creation is intentionally NOT done here. When gunicorn runs
    # multiple workers they would each call db.create_all() concurrently on an
    # empty database and race each other (duplicate pg_type entries). Tables are
    # created once at container start by init_db.py, before the workers boot.
    return app
