from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

ACTION_RISK = {
    "read": RiskLevel.LOW,
    "list": RiskLevel.LOW,
    "update_record": RiskLevel.MEDIUM,
    "send_email": RiskLevel.MEDIUM,
    "create_event": RiskLevel.MEDIUM,
    "external_message": RiskLevel.HIGH,
    "spend_money": RiskLevel.HIGH,
    "delete_data": RiskLevel.HIGH,
}
