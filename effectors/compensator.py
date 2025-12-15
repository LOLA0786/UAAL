"""
Compensator registry for reversible / undoable actions.
Used by replay, rollback, and failure recovery.
"""

from typing import Dict, Callable, Any

_COMPENSATORS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}


def register_compensator(verb: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]):
    """
    Register a compensating (undo) function for an action verb.
    """
    _COMPENSATORS[verb] = func


def run_compensator(verb: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a compensating action if available.
    """
    if verb not in _COMPENSATORS:
        return {"status": "no_undo_available"}

    try:
        return _COMPENSATORS[verb](parameters)
    except Exception as e:
        return {"status": "undo_failed", "error": str(e)}
