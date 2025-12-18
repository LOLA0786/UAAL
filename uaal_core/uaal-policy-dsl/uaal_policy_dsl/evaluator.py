def evaluate(policy: dict, action: str, payload: dict):
    for rule in policy.get("rules", []):
        condition = rule.get("if")
        if condition and action not in condition:
            continue

        if rule.get("require_approval"):
            return {
                "decision": "REQUIRE_APPROVAL",
                "reason": "human_approval_required",
            }

        allow_when = rule.get("allow_when")
        if allow_when:
            key, max_val = list(allow_when.items())[0]
            if payload.get(key) is None or payload.get(key) > max_val:
                return {
                    "decision": "DENY",
                    "reason": rule.get("deny_reason", "policy_violation"),
                }

    return {"decision": "ALLOW"}
