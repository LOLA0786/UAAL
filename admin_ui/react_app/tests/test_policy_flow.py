import policy_manager

def test_evaluate_block_gt():
    policy = {
        "id":"p1",
        "name":"block big",
        "version":1,
        "rules":[
            {"field":"intent","op":"eq","value":"purchase"},
            {"field":"parameters.amount","op":"gt","value":1000,"action":"block","require_2fa": True}
        ],
        "enabled": True
    }
    ua = {"intent":"purchase", "parameters":{"amount": 1500}}
    res = policy_manager.evaluate_policy(policy, ua)
    assert res["allowed"] == False
    assert res["require_2fa"] == True

def test_evaluate_pass():
    policy = {
        "id":"p2",
        "name":"pass",
        "version":1,
        "rules":[
            {"field":"intent","op":"eq","value":"purchase"},
            {"field":"parameters.amount","op":"gt","value":10000,"action":"block"}
        ],
        "enabled": True
    }
    ua = {"intent":"purchase", "parameters":{"amount": 1500}}
    res = policy_manager.evaluate_policy(policy, ua)
    assert res["allowed"] == True
