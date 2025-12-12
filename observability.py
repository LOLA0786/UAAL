from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from prometheus_client import multiprocess
from prometheus_client import CollectorRegistry
from typing import Dict, Any
import time

# Basic metrics
REQUEST_COUNT = Counter("uaal_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
ACTION_COUNTER = Counter("uaal_actions_total", "Actions received (increment per action)", ["actor_id"])
POLICY_VIOLATIONS = Counter("uaal_policy_violations_total", "Policy violations detected")
ACTION_LATENCY = Histogram("uaal_action_latency_seconds", "Action handling latency seconds", ["endpoint"])
RETRY_GAUGE = Gauge("uaal_retries_total", "Number of items in retry queue")
APPROVAL_QUEUE_GAUGE = Gauge("uaal_approval_queue_size", "Size of the approval queue")

def metrics_response():
    """
    Return the latest metrics in Prometheus text format.
    The caller should return a fastapi Response with media_type='text/plain'.
    """
    return generate_latest()
