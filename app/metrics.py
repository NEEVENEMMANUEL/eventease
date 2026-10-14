"""Prometheus instrumentation.

Exposes request counts and latency so Prometheus can scrape /metrics.
Node Exporter handles host-level CPU/RAM/disk/network separately.
"""
import time

from flask import request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    "eventease_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "eventease_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)


def init_app(app):
    @app.before_request
    def _start_timer():
        request._start_time = time.perf_counter()

    @app.after_request
    def _record_metrics(response):
        endpoint = request.endpoint or "unknown"
        if endpoint != "main.metrics_endpoint":
            start = getattr(request, "_start_time", None)
            if start is not None:
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(
                    time.perf_counter() - start
                )
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code,
            ).inc()
        return response


def metrics_response():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
