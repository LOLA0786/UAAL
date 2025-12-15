import pytest

from policy.decision_engine import decide_action
from models.intent import AgentIntent


class FakeConsent:
    def allows(self, verb):
        return verb != "delete_data"


class FakeContext:
    def __init__(self):
        self.spend_limit = 100
        self.max_batch_size = 10
        self.min_confidence = 0.6
        self.consent = FakeConsent()

    def is_anomalous(self, intent):
        return False


def test_low_risk_action_auto_approved():
    intent = AgentIntent(
        actor_id="agent1",
        verb="read",
        target={"type": "doc"},
        parameters={},
        confidence=0.9,
    )
    needs_approval, reason = decide_action(intent, FakeContext())
    assert needs_approval is False
    assert reason == "auto_approved"


def test_high_risk_action_requires_approval():
    intent = AgentIntent(
        actor_id="agent1",
        verb="delete_data",
        target={"type": "db"},
        parameters={},
        confidence=0.9,
    )
    needs_approval, reason = decide_action(intent, FakeContext())
    assert needs_approval is True
    assert reason == "high_risk_action"


def test_spend_limit_enforced():
    intent = AgentIntent(
        actor_id="agent1",
        verb="spend_money",
        target={"type": "payment"},
        parameters={"amount": 1000},
        confidence=0.9,
    )
    needs_approval, reason = decide_action(intent, FakeContext())
    assert needs_approval is True
    assert reason == "high_risk_action"


def test_low_confidence_triggers_approval():
    intent = AgentIntent(
        actor_id="agent1",
        verb="create_event",
        target={"type": "calendar"},
        parameters={},
        confidence=0.2,
    )
    needs_approval, reason = decide_action(intent, FakeContext())
    assert needs_approval is True
    assert reason == "low_confidence"


def test_consent_blocking():
    intent = AgentIntent(
        actor_id="agent1",
        verb="delete_data",
        target={"type": "db"},
        parameters={},
        confidence=0.95,
    )
    ctx = FakeContext()
    needs_approval, reason = decide_action(intent, ctx)
    assert needs_approval is True
