from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.log import LoginLog, OperationLog

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/login", response_model=list[dict], dependencies=[Depends(require_permissions("view_logs"))])
def get_login_logs(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)) -> list[dict]:
    logs = db.execute(select(LoginLog).order_by(LoginLog.at.desc()).limit(100)).scalars().all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "ip": log.ip,
            "success": log.success,
            "at": log.at,
        }
        for log in logs
    ]


@router.get("/ops", response_model=list[dict], dependencies=[Depends(require_permissions("view_logs"))])
def get_operation_logs(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)) -> list[dict]:
    logs = db.execute(select(OperationLog).order_by(OperationLog.at.desc()).limit(100)).scalars().all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity": log.entity,
            "entity_id": log.entity_id,
            "at": log.at,
        }
        for log in logs
    ]
