from fastapi import HTTPException
from uaal.policy import authorize
from uaal.evidence import emit_evidence

def uaal_gate(agent, action, payload, model_info=None):
    decision = authorize(
        agent=agent,
        action=action,
        payload=payload,
        model=model_info,
    )

    emit_evidence(decision)

    if not decision.allowed:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "action_blocked",
                "reason": decision.reason,
                "policy": decision.policy,
                "decision_id": decision.id,
            },
        )

    return decision
