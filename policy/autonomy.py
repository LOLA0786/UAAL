def autonomy_level(trust_score: float) -> str:
    if trust_score < 0.3:
        return "manual"
    if trust_score < 0.7:
        return "approval_required"
    return "autonomous"
