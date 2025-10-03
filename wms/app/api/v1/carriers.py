from fastapi import APIRouter, Depends

from app.core.deps import get_current_active_user, require_permissions

router = APIRouter(prefix="/carriers", tags=["carriers"])


@router.post("/rate", dependencies=[Depends(require_permissions("ship"))])
def rate_carrier(current_user=Depends(get_current_active_user)) -> dict:
    return {"rates": [{"service": "STANDARD", "amount": 10.0}]}


@router.post("/label", dependencies=[Depends(require_permissions("ship"))])
def label_carrier(current_user=Depends(get_current_active_user)) -> dict:
    return {"status": "queued"}


@router.post("/webhook")
def carrier_webhook(payload: dict) -> dict:
    return {"status": "received", "payload": payload}
