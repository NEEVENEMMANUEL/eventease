"""Integration tests covering the HTTP routes end to end."""


def test_index_loads_empty(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"No events yet" in resp.data


def test_index_lists_existing_event(client, make_event):
    make_event(name="Coding Night")
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Coding Night" in resp.data


def test_new_event_form_renders(client):
    resp = client.get("/events/new")
    assert resp.status_code == 200
    assert b"Post an event" in resp.data


def test_create_event_success_redirects(client):
    resp = client.post(
        "/events",
        data={
            "name": "Study Group",
            "organiser_contact": "org@uni.edu",
            "description": "Weekly catch-up",
            "capacity": "15",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Study Group" in resp.data
    assert b"Event created" in resp.data


def test_create_event_missing_name_fails(client):
    resp = client.post(
        "/events",
        data={"organiser_contact": "x@y.com", "capacity": "10"},
    )
    assert resp.status_code == 400
    assert b"Event name is required" in resp.data


def test_create_event_bad_capacity_fails(client):
    resp = client.post(
        "/events",
        data={"name": "Bad", "organiser_contact": "x@y.com", "capacity": "abc"},
    )
    assert resp.status_code == 400
    assert b"whole number" in resp.data


def test_create_event_zero_capacity_fails(client):
    resp = client.post(
        "/events",
        data={"name": "Bad", "organiser_contact": "x@y.com", "capacity": "0"},
    )
    assert resp.status_code == 400
    assert b"at least 1" in resp.data


def test_event_detail_renders(client, make_event):
    event = make_event(name="Picnic")
    resp = client.get("/events/%d" % event.id)
    assert resp.status_code == 200
    assert b"Picnic" in resp.data


def test_event_detail_404_for_missing(client):
    resp = client.get("/events/9999")
    assert resp.status_code == 404


def test_signup_success(client, make_event):
    event = make_event(capacity=5)
    resp = client.post(
        "/events/%d/signup" % event.id,
        data={"name": "Sam", "email": "sam@example.com"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"You&#39;re registered" in resp.data or b"registered" in resp.data


def test_signup_blocks_when_full(client, make_event, add_signup):
    event = make_event(capacity=1)
    add_signup(event, email="first@example.com")
    resp = client.post(
        "/events/%d/signup" % event.id,
        data={"name": "Late", "email": "late@example.com"},
    )
    assert resp.status_code == 409
    assert b"already full" in resp.data


def test_signup_blocks_duplicate_email(client, make_event, add_signup):
    event = make_event(capacity=10)
    add_signup(event, email="dup@example.com")
    resp = client.post(
        "/events/%d/signup" % event.id,
        data={"name": "Again", "email": "dup@example.com"},
    )
    assert resp.status_code == 409
    assert b"already registered" in resp.data


def test_signup_requires_fields(client, make_event):
    event = make_event(capacity=10)
    resp = client.post(
        "/events/%d/signup" % event.id,
        data={"name": "", "email": ""},
    )
    assert resp.status_code == 400
    assert b"both required" in resp.data


def test_full_event_shows_full_pill(client, make_event, add_signup):
    event = make_event(capacity=1)
    add_signup(event, email="one@example.com")
    resp = client.get("/events/%d" % event.id)
    assert b"Full" in resp.data


def test_footer_shows_build_info(client):
    resp = client.get("/")
    assert b"build" in resp.data
