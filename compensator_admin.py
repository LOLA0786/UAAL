from fastapi import APIRouter, Depends, HTTPException
from effectors.compensator import COMPENSATE_REGISTRY, run_compensator
import middleware_auth, middleware_rbac

router = APIRouter(prefix="/admin/compensator", tags=["compensator"])

@router.get("/list")
def list_compensators(current_user = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role("admin"))):
    return {"count": len(COMPENSATE_REGISTRY), "entries": list(COMPENSATE_REGISTRY.keys())}

@router.post("/run/{action_id}")
def run(action_id: str, current_user = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role("admin"))):
    res = run_compensator(action_id)
    if res.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="compensator not found")
    return res
