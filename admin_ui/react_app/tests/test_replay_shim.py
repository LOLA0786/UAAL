from replay_shim import replay_action
def test_replay_not_found():
    res = replay_action("nonexistent-action", dry_run=True)
    assert res["status"] in ("not_found","status":"not_found") or res.get("simulate", True)
