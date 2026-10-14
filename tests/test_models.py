"""Unit tests for the Event / Signup models (no HTTP layer)."""


def test_new_event_has_no_signups(make_event):
    event = make_event(capacity=5)
    assert event.spots_taken == 0


def test_spots_remaining_equals_capacity_when_empty(make_event):
    event = make_event(capacity=8)
    assert event.spots_remaining == 8


def test_is_full_false_when_empty(make_event):
    event = make_event(capacity=3)
    assert event.is_full is False


def test_spots_taken_counts_signups(make_event, add_signup):
    event = make_event(capacity=5)
    add_signup(event, email="a@example.com")
    add_signup(event, email="b@example.com")
    assert event.spots_taken == 2


def test_spots_remaining_decreases_with_signups(make_event, add_signup):
    event = make_event(capacity=5)
    add_signup(event, email="a@example.com")
    assert event.spots_remaining == 4


def test_is_full_true_at_capacity(make_event, add_signup):
    event = make_event(capacity=2)
    add_signup(event, email="a@example.com")
    add_signup(event, email="b@example.com")
    assert event.is_full is True


def test_spots_remaining_never_negative(make_event, add_signup):
    event = make_event(capacity=1)
    add_signup(event, email="a@example.com")
    # capacity already met; the property should clamp at zero
    assert event.spots_remaining == 0


def test_has_signup_true_for_registered_email(make_event, add_signup):
    event = make_event()
    add_signup(event, email="taken@example.com")
    assert event.has_signup("taken@example.com") is True


def test_has_signup_is_case_insensitive(make_event, add_signup):
    event = make_event()
    add_signup(event, email="Taken@Example.com")
    assert event.has_signup("taken@example.com") is True


def test_has_signup_false_for_unknown_email(make_event, add_signup):
    event = make_event()
    add_signup(event, email="someone@example.com")
    assert event.has_signup("nobody@example.com") is False


def test_has_signup_false_on_empty_input(make_event):
    event = make_event()
    assert event.has_signup("") is False


def test_has_signup_strips_whitespace(make_event, add_signup):
    event = make_event()
    add_signup(event, email="spaced@example.com")
    assert event.has_signup("  spaced@example.com  ") is True


def test_event_stores_capacity(make_event):
    event = make_event(capacity=42)
    assert event.capacity == 42


def test_event_stores_contact(make_event):
    event = make_event(contact="hello@club.org")
    assert event.organiser_contact == "hello@club.org"


def test_event_description_can_be_empty(make_event):
    event = make_event(description="")
    assert event.description == ""


def test_signup_links_to_event(make_event, add_signup):
    event = make_event()
    s = add_signup(event, name="Jo")
    assert s.event_id == event.id
    assert s.event is event


def test_multiple_signups_listed(make_event, add_signup):
    event = make_event(capacity=5)
    add_signup(event, name="One", email="1@example.com")
    add_signup(event, name="Two", email="2@example.com")
    names = [s.name for s in event.signups]
    assert "One" in names and "Two" in names


def test_is_full_when_over_subscribed(make_event, add_signup):
    event = make_event(capacity=1)
    add_signup(event, email="a@example.com")
    assert event.is_full is True


def test_spots_remaining_with_partial_fill(make_event, add_signup):
    event = make_event(capacity=10)
    for i in range(3):
        add_signup(event, email="user%d@example.com" % i)
    assert event.spots_remaining == 7


def test_event_has_created_at(make_event):
    event = make_event()
    assert event.created_at is not None
