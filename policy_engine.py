from datetime import datetime

def is_within_time_window(policy: dict) -> bool:
    if not policy or "allowed_hours" not in policy:
        return True

    start, end = policy["allowed_hours"]
    now_hour = datetime.now().hour
    return start <= now_hour < end
