# EventEase

A web application for small community groups and student societies to **post and register for events**, built to demonstrate a containerised CI/CD pipeline for **SWE40006** (Group CL02_Fri12:30_G06).

## What it does

- Public event listings showing capacity and remaining spots
- Post an event (name, organiser contact, description, capacity)
- Sign up for an event (name + email) with validation:
  - blocks registration once an event is **full**
  - blocks **duplicate** registrations with the same email
- `/health` — JSON app + database status (used for smoke tests and rollback)
- `/metrics` — Prometheus metrics (request count + latency)
- Footer **version banner** showing build number + commit SHA (proof of deployment)

## Tech stack

Flask · PostgreSQL · Gunicorn · Nginx · Docker + Compose · pytest + Playwright · Prometheus + Grafana · GitHub Actions + GHCR · AWS EC2

## Run it locally

```bash
cp .env.example .env          # adjust values if you like
docker compose up --build
# open http://localhost
```

The app runs behind Nginx on port 80, with PostgreSQL in its own container.

## Run the tests

Unit + integration (no browser, uses in-memory SQLite):

```bash
pip install -r requirements-dev.txt
pytest                         # runs with the 70% coverage gate in CI
```

End-to-end (Playwright, against a running deployment):

```bash
playwright install chromium
BASE_URL=http://localhost pytest tests/e2e -m e2e
```

Lint:

```bash
flake8 .
```

## The pipeline

`git push` to `main` triggers `.github/workflows/ci.yml`:

1. **test** — flake8 + pytest with coverage gate (fails below 70%), integration tests run against a Postgres service container.
2. **build-and-push** — builds one Docker image, tags it with the commit SHA, pushes to GHCR.
3. **deploy-staging** — pulls that exact image onto the Staging EC2, smoke-tests `/health`, runs the Playwright E2E suite.
4. **deploy-production** — promotes the **same** image to Production, health-checks it, and **auto-rolls back** to the previous image if the check fails. Posts the result to Discord.

### Secrets to configure in GitHub (Settings → Secrets → Actions)

`STAGING_HOST`, `PROD_HOST`, `EC2_USER`, `EC2_SSH_KEY`, `GHCR_TOKEN`, `DISCORD_WEBHOOK`.

On each EC2 instance: install Docker + Compose, clone this repo to `~/eventease`, and copy `docker-compose.yml`, `nginx/`, and `.env` there.

## Project structure

```
app/            Flask application (factory, models, routes, metrics, templates, static)
tests/          unit + integration (pytest) and e2e (Playwright)
nginx/          reverse-proxy config
monitoring/     Prometheus scrape config
.github/        CI/CD workflow
Dockerfile, docker-compose.yml
```
