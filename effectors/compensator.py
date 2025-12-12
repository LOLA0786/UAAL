"""
Compensating actions registry and simple orchestrator.
For each delivered effector, register a compensating function to undo the effect.
"""
COMPENSATE_REGISTRY = {}

def register_compensator(action_id: str, fn, *args, **kwargs):
    COMPENSATE_REGISTRY[action_id] = (fn, args, kwargs)

def run_compensator(action_id: str):
    if action_id not in COMPENSATE_REGISTRY:
        return {"status": "not_found"}
    fn, args, kwargs = COMPENSATE_REGISTRY.pop(action_id)
    try:
        res = fn(*args, **kwargs)
        return {"status": "ok", "result": res}
    except Exception as e:
        return {"status": "error", "error": str(e)}
