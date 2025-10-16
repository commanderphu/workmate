# app/routers/hr.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io
import csv

from app.database import get_db
from app.core.auth import get_current_user
from app.core.roles import require_roles
from app.core.audit import log_action
from app import models
from app.services import hr_service
from app.schemas import HROverview


router = APIRouter(prefix="/hr", tags=["HR"])


# ============================================================
# 🧩 HR Overview (Dashboard KPIs)
# ============================================================
@router.get("/overview", response_model=HROverview)
@require_roles(["management", "hr"])
async def hr_overview(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Liefert HR-KPIs als Subset der Dashboard-Aggregation."""
    print(f"[HR] Overview called by {user.get('email')}")
    return hr_service.get_hr_overview(db)


# ============================================================
# 🧮 Department Stats
# ============================================================
@router.get("/stats/departments")
@require_roles(["management", "hr"])
async def hr_stats_departments(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Liefert aggregierte Mitarbeiterzahlen pro Abteilung."""
    data = hr_service.get_hr_overview(db)
    return data["departments"]


# ============================================================
# 🧾 HR Report Export (CSV / JSON)
# ============================================================
@router.get("/reports/export", response_class=StreamingResponse)
@require_roles(["management", "hr"])
async def export_hr_report(
    format: str = Query("csv", enum=["csv", "json"]),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Exportiert HR-Daten (CSV oder JSON)."""
    print(f"[HR] Export triggered by {user.get('email')} ({format})")

    # 🪵 Audit-Log für Exportvorgang
    log_action(
        db=db,
        user=user,
        action="hr_export_report",
        resource="hr_reports",
        details={"format": format},
    )
    db.commit()

    return hr_service.export_hr_report(db, user, format)


# ============================================================
# 🧩 HR Audit History (inkl. Dokument- & Reminder-Logs)
# ============================================================
@router.get("/audits")
@require_roles(["management", "hr"])
def get_hr_audits(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Gibt alle HR-relevanten Audit-Einträge zurück:
    - HR-spezifische (resource LIKE 'hr_%')
    - Dokumente (document:%)
    - Reminder (reminder:%)
    """
    query = (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.resource.ilike("hr_%")
            | models.AuditLog.resource.ilike("document:%")
            | models.AuditLog.resource.ilike("reminder:%")
        )
        .order_by(models.AuditLog.created_at.desc())
    )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {"total": total, "items": items}


# ============================================================
# 📤 HR Audit CSV Export
# ============================================================
@router.get("/audits/export", response_class=StreamingResponse)
@require_roles(["management", "hr"])
def export_hr_audits(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Exportiert HR-bezogene Audit-Einträge als CSV.
    - Nur HR & Management
    - Trennt HR-Audits klar von Admin-Logs
    """
    logs = (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.resource.ilike("hr_%")
            | models.AuditLog.resource.ilike("document:%")
            | models.AuditLog.resource.ilike("reminder:%")
        )
        .order_by(models.AuditLog.created_at.desc())
        .all()
    )

    if not logs:
        raise HTTPException(status_code=404, detail="Keine HR-Audit-Logs gefunden")

    # 🪵 Audit über Audit
    log_action(
        db=db,
        user=user,
        action="hr_export_audits",
        resource="hr_audits",
        details={"entries": len(logs)},
    )
    db.commit()

    # ❗ StringIO ohne encoding/newline
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
        iter([output.getvalue().encode("utf-8")]),  # hier sauber nach UTF-8
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=hr_audits.csv"},
)