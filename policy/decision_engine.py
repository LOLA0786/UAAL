from policy.risk_model import ACTION_RISK, RiskLevel

def decide_action(intent, context):
    risk = ACTION_RISK.get(intent.verb, RiskLevel.HIGH)

    if risk == RiskLevel.HIGH:
        return True, "high_risk_action"

    amount = intent.parameters.get("amount", 0)
    if amount > context.spend_limit:
        return True, "spend_limit_exceeded"

    batch_size = intent.parameters.get("batch_size")
    if batch_size and batch_size > context.max_batch_size:
        return True, "large_blast_radius"

    if intent.confidence is not None and intent.confidence < context.min_confidence:
        return True, "low_confidence"

    if context.is_anomalous(intent):
        return True, "anomalous_behavior"

    if not context.consent.allows(intent.verb):
        return True, "no_consent"

    return False, "auto_approved"
