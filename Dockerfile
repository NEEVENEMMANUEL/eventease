# Build once, deploy many: the same image runs in every environment.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so Docker can cache this layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user for better security.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Build metadata, injected by the CI pipeline at build time.
ARG BUILD_NUMBER=local
ARG GIT_SHA=dev
ENV BUILD_NUMBER=$BUILD_NUMBER \
    GIT_SHA=$GIT_SHA \
    FLASK_ENV=production

EXPOSE 8000

# Create the tables once (init_db.py), then start gunicorn. Doing the table
# creation before the workers boot avoids a concurrent-create race between them.
# 3 workers is plenty for a t3.small; tune with the WEB_CONCURRENCY env var.
CMD ["sh", "-c", "python init_db.py && exec gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:app"]
