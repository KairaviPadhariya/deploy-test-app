"""
Demo Application — Week 7
A minimal Flask app deployed into Minikube that exposes real Prometheus
metrics at /metrics. This is what the monitoring_service/collector.py
queries for error_rate and latency data.

Two modes:
  - Normal (default):    low error rate (~0%), fast responses
  - Anomalous:           SIMULATE_ANOMALY=true → high error rate (~50%),
                         slow responses (~2s) → triggers auto-rollback

The app uses prometheus_client to expose:
  - http_requests_total{method, endpoint, status}  (Counter)
  - http_request_duration_seconds{method, endpoint}  (Histogram)

These are the standard metric names the collector's PromQL queries expect.
"""
import os
import random
import time

from flask import Flask, Response, jsonify
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

app = Flask(__name__)

# ── Prometheus instrumentation ────────────────────────────────────────
# Use a custom registry so we don't pollute metrics with Python GC stats
# that would confuse the collector's queries.
REGISTRY = CollectorRegistry()

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=REGISTRY,
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=REGISTRY,
)

# ── Anomaly simulation toggle ────────────────────────────────────────
SIMULATE_ANOMALY = os.getenv("SIMULATE_ANOMALY", "false").lower() == "true"
if SIMULATE_ANOMALY:
    print("[DEMO APP] *** ANOMALY MODE ACTIVE — high error rate + slow responses ***")
else:
    print("[DEMO APP] Normal mode — healthy responses")


@app.route("/")
def index():
    """Main endpoint — simulates a real request with timing."""
    start = time.time()

    if SIMULATE_ANOMALY:
        # Slow response + 50% chance of 500 error
        time.sleep(random.uniform(1.5, 3.0))
        if random.random() < 0.5:
            duration = time.time() - start
            REQUEST_COUNT.labels(method="GET", endpoint="/", status="500").inc()
            REQUEST_DURATION.labels(method="GET", endpoint="/").observe(duration)
            return jsonify({"error": "simulated server error"}), 500
    else:
        # Fast, healthy response
        time.sleep(random.uniform(0.001, 0.02))

    duration = time.time() - start
    REQUEST_COUNT.labels(method="GET", endpoint="/", status="200").inc()
    REQUEST_DURATION.labels(method="GET", endpoint="/").observe(duration)
    return jsonify({
        "status": "ok",
        "app": "predictive-auto-deploy-demo",
        "anomaly_mode": SIMULATE_ANOMALY,
    })


@app.route("/health")
def health():
    """Kubernetes readiness/liveness probe endpoint."""
    REQUEST_COUNT.labels(method="GET", endpoint="/health", status="200").inc()
    return jsonify({"status": "healthy"})


@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint — returns metrics in exposition format."""
    return Response(
        generate_latest(REGISTRY),
        mimetype=CONTENT_TYPE_LATEST,
    )


@app.route("/generate-traffic")
def generate_traffic():
    """Hit this once to generate a burst of requests (useful for seeding
    metrics so Prometheus has data to scrape on the next interval)."""
    results = {"total": 20, "success": 0, "error": 0}
    for _ in range(20):
        start = time.time()
        if SIMULATE_ANOMALY and random.random() < 0.5:
            time.sleep(random.uniform(1.0, 2.0))
            duration = time.time() - start
            REQUEST_COUNT.labels(method="GET", endpoint="/", status="500").inc()
            REQUEST_DURATION.labels(method="GET", endpoint="/").observe(duration)
            results["error"] += 1
        else:
            time.sleep(random.uniform(0.001, 0.01))
            duration = time.time() - start
            REQUEST_COUNT.labels(method="GET", endpoint="/", status="200").inc()
            REQUEST_DURATION.labels(method="GET", endpoint="/").observe(duration)
            results["success"] += 1
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
