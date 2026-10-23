"""Database models for EventEase."""
from datetime import datetime

from app import db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    organiser_contact = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    signups = db.relationship(
        "Signup", backref="event", cascade="all, delete-orphan", lazy="select"
    )
#error popup 1

    @property
    def spots_taken(self):
        return len(self.signups)

    @property
    def spots_remaining(self):
        return max(self.capacity - self.spots_taken, 0)

    @property
    def is_full(self):
        return self.spots_taken >= self.capacity

    def has_signup(self, email):
        email = (email or "").strip().lower()
        return any(s.email.lower() == email for s in self.signups)


class Signup(db.Model):
    __tablename__ = "signups"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
