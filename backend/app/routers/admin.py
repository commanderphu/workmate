# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io, csv

from app.database import get_db
from app.models import AuditLog
from app.core.auth import get_current_user
from app.core.roles import require_roles
from app.core.audit import log_action

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================================
# 📄 Audit-Logs (Liste + Filter + Pagination)
# ============================================================
@router.get("/audits")
@require_roles(["management", "admin"])
def get_audits(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    user_email: str | None = Query(None, description="Filter by user email"),
    action: str | None = Query(None, description="Filter by action"),
    resource: str | None = Query(None, description="Filter by resource"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Listet alle Audit-Logs mit optionalen Filtern auf (Admin & Management only)."""
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
# 📤 CSV-Export (inkl. Audit über Audit)
# ============================================================
@router.get("/audits/export", response_class=StreamingResponse)
@require_roles(["management", "admin"])
def export_audits(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Exportiert alle Audit-Logs als CSV-Datei."""
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
    if not logs:
        raise HTTPException(status_code=404, detail="Keine Audit-Logs gefunden")

    # 🪵 Audit über Audit (Export protokollieren)
    log_action(
        db=db,
        user=user,
        action="admin_export_audits",
        resource="admin_audits",
        details={"entries": len(logs)},
    )
    db.commit()

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["created_at", "user_email", "role", "action", "resource", "details"])

    for log in logs:
        writer.writerow([
            log.created_at.isoformat() if log.created_at else None,
            log.user_email,
            log.role,
            log.action,
            log.resource,
            log.details,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue().encode("utf-8")]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )
