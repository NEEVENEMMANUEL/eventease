"""Create database tables once, before the gunicorn workers start.

Running this as a single step (rather than inside create_app, which every
gunicorn worker calls) avoids a race where multiple workers try to create the
same tables at the same moment on a fresh database and collide. It is safe to
run repeatedly: db.create_all() only creates tables that don't already exist.
"""
from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()

print("EventEase: database tables are ready.")
