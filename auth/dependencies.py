from fastapi import Header, HTTPException

def require_role(required_role: str):
    def checker(x_role: str = Header(None)):
        if x_role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return x_role
    return checker

# Backward-compatible admin dependency
def require_admin(x_role: str = Header(None)):
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return x_role
