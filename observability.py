from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
)
from prometheus_client import multiprocess, CollectorRegistry
from prometheus_client import Gauge
from typing import Dict

REQUEST_COUNT = Counter(
    "uaal_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "uaal_request_latency_seconds", "Request latency in seconds", ["endpoint"]
)
ACTION_COUNT = Counter("uaal_actions_total", "Total actions received", ["actor_id"])


def metrics_response():
    return generate_latest()
