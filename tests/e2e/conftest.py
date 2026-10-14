"""E2E tests use pytest-playwright's own fixtures (page, browser).

Kept separate from the unit/integration conftest so running
`pytest tests` (unit + integration) never spins up a browser.
"""
