from dataclasses import dataclass
from datetime import datetime
import uuid

# ------------------------
# Decision Object
# ------------------------

@dataclass
class Decision:
    id: str
    agent: str
    action: str
    payload: dict
    allowed: bool
    reason: str
    policy: str
    timestamp: str


# ------------------------
# UAAL Authorization Core
# ------------------------

def authorize(agent: str, action: str, payload: dict, model: dict = None) -> Decision:
    """
    Core UAAL authorization hook.
    Enforces deterministic business policies.
    """

    allowed = True
    reason = "allowed_by_default"
    policy_id = "default-policy-v0"

    # ---- Pricing Policy ----
    if action == "update_price":
        new_price = payload.get("new_price")

        policy_id = "pricing-policy-v1"

        if new_price is None:
            allowed = False
            reason = "missing_price"
        elif new_price > 150:
            allowed = False
            reason = "price_above_limit"
        elif new_price < 50:
            allowed = False
            reason = "price_below_limit"
        else:
            allowed = True
            reason = "price_within_limits"

    # ---- Email Policy Example ----
    if action == "send_invoice":
        policy_id = "email-policy-v1"
        if "invoice_id" not in payload:
            allowed = False
            reason = "missing_invoice_id"

    return Decision(
        id=str(uuid.uuid4()),
        agent=agent,
        action=action,
        payload=payload,
        allowed=allowed,
        reason=reason,
        policy=policy_id,
        timestamp=datetime.utcnow().isoformat(),
    )
