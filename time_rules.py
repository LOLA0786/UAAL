from datetime import datetime

def night_freeze():
    hour = datetime.utcnow().hour
    return hour >= 22 or hour < 6
