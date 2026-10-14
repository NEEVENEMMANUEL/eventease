import pytest

from app import create_app, db as _db
from app.models import Event, Signup


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def make_event(db):
    def _make(name="Community BBQ", capacity=10, contact="org@example.com", description="Fun"):
        event = Event(
            name=name,
            organiser_contact=contact,
            description=description,
            capacity=capacity,
        )
        db.session.add(event)
        db.session.commit()
        return event
    return _make


@pytest.fixture
def add_signup(db):
    def _add(event, name="Alex", email="alex@example.com"):
        s = Signup(event_id=event.id, name=name, email=email)
        db.session.add(s)
        db.session.commit()
        return s
    return _add
