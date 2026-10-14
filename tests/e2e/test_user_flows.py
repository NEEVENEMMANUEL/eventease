"""End-to-end user-flow tests (Playwright).

These run against a live deployment (the Staging server in the pipeline).
Set BASE_URL to the target, e.g. BASE_URL=http://staging.example.com.
Run with:  pytest tests/e2e -m e2e
"""
import os
import uuid

import pytest

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

pytestmark = pytest.mark.e2e


def test_visitor_can_see_events_page(page):
    page.goto(BASE_URL + "/")
    assert "EventEase" in page.title()
    assert page.get_by_role("heading", name="Upcoming events").is_visible()


def test_organiser_can_create_an_event(page):
    unique = "E2E Launch " + uuid.uuid4().hex[:6]
    page.goto(BASE_URL + "/events/new")
    page.fill("input[name='name']", unique)
    page.fill("input[name='organiser_contact']", "e2e@example.com")
    page.fill("textarea[name='description']", "Created by an automated test.")
    page.fill("input[name='capacity']", "25")
    page.click("button[type='submit']")
    # we should land on the new event's detail page
    assert page.get_by_role("heading", name=unique).is_visible()


def test_attendee_can_sign_up(page):
    # create an event, then register for it
    unique = "E2E Signup " + uuid.uuid4().hex[:6]
    page.goto(BASE_URL + "/events/new")
    page.fill("input[name='name']", unique)
    page.fill("input[name='organiser_contact']", "e2e@example.com")
    page.fill("input[name='capacity']", "10")
    page.click("button[type='submit']")

    page.fill("input[name='name']", "Test Attendee")
    page.fill("input[name='email']", "attendee+" + uuid.uuid4().hex[:6] + "@example.com")
    page.click("button:has-text('Register')")
    assert page.get_by_text("registered").is_visible()
