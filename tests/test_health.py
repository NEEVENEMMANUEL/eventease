"""Tests for the /health and /metrics operational endpoints."""
import json


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = json.loads(resp.data)
    assert body["status"] == "ok"
    assert body["database"] == "connected"


def test_health_content_type_json(client):
    resp = client.get("/health")
    assert resp.content_type.startswith("application/json")


def test_metrics_endpoint_exposes_prometheus(client):
    # generate some traffic first so counters exist
    client.get("/")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"eventease_http_requests_total" in resp.data
