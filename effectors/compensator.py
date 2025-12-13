from typing import Dict, Callable


_COMPENSATORS = {}


def register_compensator(verb: str, func: Callable[[Dict], Dict]):
    _COMPENSATORS[verb] = func


def undo_action(action) -> Dict:
    verb = action.verb
    if verb not in _COMPENSATORS:
        return {"status": "no_undo_available"}

    return _COMPENSATORS[verb](action.parameters)
