import os
import sys

# The platform runs pytest INSIDE the built image. In scenario 4 the Dockerfile
# sets ENV SIMULATE_ANOMALY=true, which would make "/" randomly return 500 and
# fail the tests (so the bad release would never deploy). Force healthy mode for
# the test run only; the running container still uses the Dockerfile value.
os.environ["SIMULATE_ANOMALY"] = "false"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app  # noqa: E402


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