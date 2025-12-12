import uuid
import datetime


def _make_base(actor_id="agent:unknown", actor_type="agent", display_name=None):
    return {
        "action_id": str(uuid.uuid4()),
        "actor": {
            "id": actor_id,
            "type": actor_type,
            "display_name": display_name or actor_id,
        },
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "metadata": {},
    }


def openai_assistant_adapter(agent_output: dict) -> dict:
    """Adapter for an OpenAI-style assistant JSON output.
    Expects fields like: {'assistant_id':..., 'intent': 'create_event', 'target': {...}, 'explanation': '...','confidence':0.87}
    """
    base = _make_base(actor_id=agent_output.get("assistant_id", "openai:assistant"))
    verb = agent_output.get("intent") or agent_output.get("verb") or "unknown:action"
    obj = {
        "type": agent_output.get("target", {}).get("type", "unknown"),
        "id": agent_output.get("target", {}).get("id") or "",
        "attributes": agent_output.get("target", {}).get("attributes", {}),
    }
    action = {
        **base,
        "verb": verb,
        "object": obj,
        "parameters": agent_output.get(
            "params", agent_output.get("target", {}).get("attributes", {})
        ),
        "confidence": float(agent_output.get("confidence", 0.0)),
        "reasoning": agent_output.get("explanation", ""),
        "policy_evaluation": agent_output.get("policy", {}),
        "metadata": agent_output.get("meta", {}),
    }
    return action


def simple_chat_agent_adapter(agent_output: dict) -> dict:
    """Adapter for a simple custom agent that returns text like:
    {'agent':'mybot','action':'update_crm','payload':{'lead_id':'L123','fields':{...}}, 'note':'because...'}
    """
    base = _make_base(actor_id=agent_output.get("agent", "custom:agent"))
    verb = agent_output.get("action", "unknown:action")
    payload = agent_output.get("payload", {})
    obj = {
        "type": payload.get("object_type", "resource"),
        "id": payload.get("id", ""),
        "attributes": payload.get("fields", {}),
    }
    action = {
        **base,
        "verb": verb,
        "object": obj,
        "parameters": payload,
        "confidence": float(agent_output.get("confidence", 0.0)),
        "reasoning": agent_output.get("note", ""),
        "policy_evaluation": agent_output.get("policy", {}),
        "metadata": agent_output.get("meta", {}),
    }
    return action


Adapters = {
    "openai_assistant": openai_assistant_adapter,
    "simple_chat": simple_chat_agent_adapter,
}
