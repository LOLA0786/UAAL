def require_role(user, role):
    if user.role != role:
        raise PermissionError("Insufficient privileges")
