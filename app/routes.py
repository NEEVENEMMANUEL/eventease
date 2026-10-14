"""Routes for EventEase."""
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from sqlalchemy import text

from app import db
from app.models import Event, Signup
from app import metrics

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template("index.html", events=events)


@bp.route("/events/new", methods=["GET"])
def new_event():
    return render_template("new_event.html")


@bp.route("/events", methods=["POST"])
def create_event():
    name = (request.form.get("name") or "").strip()
    contact = (request.form.get("organiser_contact") or "").strip()
    description = (request.form.get("description") or "").strip()
    capacity_raw = (request.form.get("capacity") or "").strip()

    errors = []
    if not name:
        errors.append("Event name is required.")
    if not contact:
        errors.append("Organiser contact is required.")

    capacity = None
    try:
        capacity = int(capacity_raw)
        if capacity < 1:
            errors.append("Capacity must be at least 1.")
    except ValueError:
        errors.append("Capacity must be a whole number.")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("new_event.html"), 400

    event = Event(
        name=name,
        organiser_contact=contact,
        description=description,
        capacity=capacity,
    )
    db.session.add(event)
    db.session.commit()
    flash("Event created.", "success")
    return redirect(url_for("main.event_detail", event_id=event.id))


@bp.route("/events/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("event_detail.html", event=event)


@bp.route("/events/<int:event_id>/signup", methods=["POST"])
def signup(event_id):
    event = Event.query.get_or_404(event_id)

    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()

    if not name or not email:
        flash("Name and email are both required.", "error")
        return render_template("event_detail.html", event=event), 400

    if event.is_full:
        flash("Sorry, this event is already full.", "error")
        return render_template("event_detail.html", event=event), 409

    if event.has_signup(email):
        flash("That email is already registered for this event.", "error")
        return render_template("event_detail.html", event=event), 409

    db.session.add(Signup(event_id=event.id, name=name, email=email))
    db.session.commit()
    flash("You're registered. See you there!", "success")
    return redirect(url_for("main.event_detail", event_id=event.id))


@bp.route("/health")
def health():
    """Reports app status and database connectivity for the pipeline."""
    db_ok = True
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    status = "ok" if db_ok else "degraded"
    code = 200 if db_ok else 503
    return jsonify(status=status, database="connected" if db_ok else "unreachable"), code


@bp.route("/metrics")
def metrics_endpoint():
    return metrics.metrics_response()
