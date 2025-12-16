def allow(message, explanation=None):
    return {
        "decision": "allow",
        "message": message,
        "explanation": explanation
    }

def deny(reason, message, explanation=None):
    return {
        "decision": "deny",
        "reason": reason,
        "message": message,
        "explanation": explanation
    }
