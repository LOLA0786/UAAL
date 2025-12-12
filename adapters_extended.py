"""Adapters that convert various agent outputs into a normalized action dict (UAS)."""
from typing import Any, Dict
import uuid
import datetime


def _make_base(
    actor_id: str = "agent:unknown", actor_type: str = "agent", display_name: str = None
) -> Dict[str, Any]:
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


def openai_assistant_adapter(agent_output: Dict[str, Any]) -> Dict[str, Any]:
    base = _make_base(actor_id=agent_output.get("assistant_id", "openai:assistant"))
    verb = agent_output.get("intent") or agent_output.get("verb") or "unknown:action"
    tgt = agent_output.get("target", {})
    obj = {
        "type": tgt.get("type", "unknown"),
        "id": tgt.get("id", ""),
        "attributes": tgt.get("attributes", {}),
    }
    return {
        **base,
        "verb": verb,
        "object": obj,
        "parameters": agent_output.get("params", tgt.get("attributes", {})),
        "confidence": float(agent_output.get("confidence", 0.0) or 0.0),
        "reasoning": agent_output.get("explanation", ""),
        "policy_evaluation": agent_output.get("policy", {}),
        "metadata": agent_output.get("meta", {}),
    }


def anthropic_adapter(agent_output: Dict[str, Any]) -> Dict[str, Any]:
    base = _make_base(actor_id=agent_output.get("assistant_id", "anthropic:assistant"))
    verb = (
        agent_output.get("intent") or agent_output.get("action") or "anthropic:unknown"
    )
    tgt = agent_output.get("target", {})
    obj = {
        "type": tgt.get("type", "unknown"),
        "id": tgt.get("id", ""),
        "attributes": tgt.get("attributes", {}),
    }
    return {
        **base,
        "verb": verb,
        "object": obj,
        "parameters": agent_output.get("params", {}),
        "confidence": float(agent_output.get("confidence", 0.0) or 0.0),
        "reasoning": agent_output.get("rationale", agent_output.get("explanation", "")),
        "policy_evaluation": agent_output.get("policy", {}),
        "metadata": agent_output.get("meta", {}),
    }


def google_gemini_adapter(agent_output: Dict[str, Any]) -> Dict[str, Any]:
    base = _make_base(actor_id=agent_output.get("agent_id", "gemini:assistant"))
    verb = agent_output.get("action", "gemini:unknown")
    entity = agent_output.get("entity", {})
    obj = {
        "type": entity.get("type", "unknown"),
        "id": entity.get("id", ""),
        "attributes": entity.get("attributes", {}),
    }
    return {
        **base,
        "verb": verb,
        "object": obj,
        "parameters": entity.get("attributes", {}),
        "confidence": float(
            agent_output.get("score", agent_output.get("confidence", 0.0)) or 0.0
        ),
        "reasoning": agent_output.get("why", ""),
        "policy_evaluation": agent_output.get("policy", {}),
        "metadata": agent_output.get("meta", {}),
    }


def llama_adapter(agent_output: Dict[str, Any]) -> Dict[str, Any]:
    base = _make_base(actor_id=agent_output.get("agent", "llama:agent"))
    verb = agent_output.get("do", agent_output.get("action", "llama:unknown"))
    target = agent_output.get("target", {})
    obj = {
        "type": target.get("type", "resource"),
        "id": target.get("id", ""),
        "attributes": target.get("attributes", {}),
    }
    return {
        **base,
        "verb": verb,
        "object": obj,
        "parameters": agent_output.get("params", target.get("attributes", {})),
        "confidence": float(agent_output.get("confidence", 0.0) or 0.0),
        "reasoning": agent_output.get("explanation", agent_output.get("note", "")),
        "policy_evaluation": agent_output.get("policy", {}),
        "metadata": agent_output.get("meta", {}),
    }


def openai_tools_adapter(agent_output: Dict[str, Any]) -> Dict[str, Any]:
    base = _make_base(actor_id=agent_output.get("assistant_id", "openai:functions"))
    verb = agent_output.get("name", "openai:tool")
    args = agent_output.get("arguments", {})
    obj = {
        "type": args.get("object_type", "resource"),
        "id": args.get("id", ""),
        "attributes": args,
    }
    return {
        **base,
        "verb": verb,
        "object": obj,
        "parameters": args,
        "confidence": float(
            agent_output.get("confidence", 0.0) or agent_output.get("score", 0.0) or 0.0
        ),
        "reasoning": agent_output.get("explanation", ""),
        "policy_evaluation": agent_output.get("policy", {}),
        "metadata": agent_output.get("meta", {}),
    }


def react_adapter(agent_output: Dict[str, Any]) -> Dict[str, Any]:
    base = _make_base(actor_id=agent_output.get("agent", "react:agent"))
    action = agent_output.get("action", {})
    verb = action.get("tool", action.get("action", "react:action"))
    input_ = action.get("input", {})
    obj = {
        "type": input_.get("object_type", "resource"),
        "id": input_.get("id", ""),
        "attributes": input_,
    }
    return {
        **base,
        "verb": verb,
        "object": obj,
        "parameters": input_,
        "confidence": float(agent_output.get("confidence", 0.0) or 0.0),
        "reasoning": agent_output.get(
            "chain_of_thought", agent_output.get("reason", "")
        ),
        "policy_evaluation": agent_output.get("policy", {}),
        "metadata": agent_output.get("meta", {}),
    }


Adapters = {
    "openai_assistant": openai_assistant_adapter,
    "openai_tools": openai_tools_adapter,
    "anthropic": anthropic_adapter,
    "gemini": google_gemini_adapter,
    "llama": llama_adapter,
    "react": react_adapter,
}
