# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuditLog
from app.core.auth import get_current_user
import io, csv
from app.core.roles import require_roles

router = APIRouter(prefix="/admin", tags=["Admin"])

# ============================================================
# 📄 Audit-Logs (Liste + Filter + Pagination)
# ============================================================

@router.get("/audits")
@require_roles(["management","admin"])
def get_audits(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    user_email: str | None = None,
    action: str | None = None,
    resource: str | None = None,
    skip: int = 0,
    limit: int = 50,
):

    query = db.query(AuditLog)
    if user_email:
        query = query.filter(AuditLog.user_email.ilike(f"%{user_email}%"))
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if resource:
        query = query.filter(AuditLog.resource.ilike(f"%{resource}%"))

    total = query.count()
    items = (
        query.order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"total": total, "items": items}


# ============================================================
# ⬇ CSV-Export
# ============================================================
@router.get("/audits/export")
def export_audits(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ["management", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")

    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["created_at", "user_email", "role", "action", "resource", "details"])

    for log in logs:
        writer.writerow([
            log.created_at,
            log.user_email,
            log.role,
            log.action,
            log.resource,
            log.details,
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )
