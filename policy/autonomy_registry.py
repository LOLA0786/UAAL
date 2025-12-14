from policy.autonomy import AutonomyScore

AUTONOMY_REGISTRY: dict[str, AutonomyScore] = {}

def get_score(agent_id):
    if agent_id not in AUTONOMY_REGISTRY:
        AUTONOMY_REGISTRY[agent_id] = AutonomyScore()
    return AUTONOMY_REGISTRY[agent_id]
