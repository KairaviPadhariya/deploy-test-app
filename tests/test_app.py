import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app


def test_health():
    r = app.test_client().get("/health")
    assert r.status_code == 200


def test_index_ok():
    r = app.test_client().get("/")
    assert r.status_code == 200


def test_metrics_exposed():
    app.test_client().get("/")
    r = app.test_client().get("/metrics")
    assert b"http_requests_total" in r.data
