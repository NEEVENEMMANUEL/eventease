"""Application configuration.

Settings are read from environment variables so the same image can run
unchanged in every environment (dev, test, staging, production) and only
the config differs between them.
"""
import os


def _database_url():
    url = os.environ.get("DATABASE_URL", "postgresql://eventease:eventease@db:5432/eventease")
    # SQLAlchemy 1.4+ expects the postgresql:// scheme rather than postgres://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Shown in the page footer as proof of which build is deployed.
    BUILD_NUMBER = os.environ.get("BUILD_NUMBER", "local")
    GIT_SHA = os.environ.get("GIT_SHA", "dev")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    # Unit tests run against an in-memory SQLite DB so they are fast and need
    # no external services. Integration tests in CI use a real Postgres
    # service container via DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    WTF_CSRF_ENABLED = False


class StagingConfig(BaseConfig):
    DEBUG = False


class ProductionConfig(BaseConfig):
    DEBUG = False


_CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    name = name or os.environ.get("FLASK_ENV", "development")
    return _CONFIGS.get(name, DevelopmentConfig)
