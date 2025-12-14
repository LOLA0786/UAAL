from fastapi import APIRouter
from policy.approval_queue import APPROVAL_QUEUE
from observability.telemetry import stats

router = APIRouter(prefix="/admin")

@router.get("/approvals")
def list_approvals():
    return list(APPROVAL_QUEUE.values())

@router.get("/telemetry")
def telemetry_stats():
    return stats()
