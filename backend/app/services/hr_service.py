# app/services/hr_service.py
from __future__ import annotations

import io
import csv
import json
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app import models
from app.routers.dashboard import get_dashboard_overview
from app.core.audit import log_action


# ============================================================
# 🧭 HR Overview (Dashboard Subset)
# ============================================================
def get_hr_overview(db: Session):
    """
    Aggregiert HR-relevante Kennzahlen basierend auf dem Dashboard-Endpoint.
    """
    data = get_dashboard_overview(db)

    return {
        "employees_total": data["employees"]["total"],
        "departments": [
            {"department": dept, "count": count}
            for dept, count in data["employees"]["by_department"].items()
        ],
        "open_vacations": data["vacations"]["open_requests"],
        "active_sick_leaves": data["sick_leaves"]["active_now"],
        "documents_total": data["documents"]["total"],
        "reminders_pending": data["reminders"]["pending_total"],
        "reminders_overdue": data["reminders"]["overdue"],
        "generated_at": data["generated_at"],
    }


# ============================================================
# 📤 HR Report Export (CSV / JSON)
# ============================================================
def export_hr_report(db: Session, user: dict, format: str = "csv"):
    """
    Erstellt einen vollständigen HR-Report mit allen Kern-Tabellen und zugehörigen Audit-Einträgen.
    - Employees, Vacations, SickLeaves, Reminders
    - Enthält Audit-Logs (Ressourcen mit 'hr_' oder 'document:')
    - Export als CSV oder JSON
    """

    # ------------------------------
    # 🧾 Datensammlung
    # ------------------------------
    employees = db.query(models.Employee).all()
    vacations = db.query(models.VacationRequest).all()
    sick_leaves = db.query(models.SickLeave).all()
    reminders = db.query(models.Reminder).all()

    # 🔍 HR-bezogene Audit-Logs abrufen
    hr_audits = (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.resource.ilike("hr_%")
            | models.AuditLog.resource.ilike("document:%")
            | models.AuditLog.resource.ilike("reminder:%")
        )
        .order_by(models.AuditLog.created_at.desc())
        .limit(100)
        .all()
    )

    # ------------------------------
    # 📊 Datenstruktur
    # ------------------------------
    report_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": user.get("email"),
        "employees": [
            {
                "id": e.employee_id,
                "name": e.name,
                "department": e.department,
                "position": e.position,
                "created": e.created.isoformat() if e.created else None,
            }
            for e in employees
        ],
        "vacations": [
            {
                "id": v.id,
                "employee_id": v.employee_id,
                "status": v.status,
                "start_date": v.start_date,
                "end_date": v.end_date,
            }
            for v in vacations
        ],
        "sick_leaves": [
            {
                "id": s.id,
                "employee_id": s.employee_id,
                "document_id": s.document_id,
                "start_date": s.start_date,
                "end_date": s.end_date,
                "notes": s.notes,
                "created": s.created.isoformat() if s.created else None,
                "updated": s.updated.isoformat() if s.updated else None,
            }
            for s in sick_leaves
        ],
        "reminders": [
            {
                "id": r.id,
                "employee_id": r.employee_id,
                "status": r.status,
                "title": r.title,
                "due_date": r.due_date,
            }
            for r in reminders
        ],
        "audits": [
            {
                "id": a.id,
                "user_email": a.user_email,
                "role": a.role,
                "action": a.action,
                "resource": a.resource,
                "details": a.details,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in hr_audits
        ],
    }

    # ------------------------------
    # 🪵 Audit-Log: Export-Aktion speichern
    # ------------------------------
    log_action(
        db=db,
        user=user,
        action="hr_export",
        resource="hr_reports",
        details={
            "format": format,
            "employees": len(employees),
            "vacations": len(vacations),
            "sick_leaves": len(sick_leaves),
            "reminders": len(reminders),
            "audits": len(hr_audits),
        },
    )
    db.commit()

    # ------------------------------
    # 📤 JSON Export
    # ------------------------------
    if format == "json":
        json_data = json.dumps(report_data, ensure_ascii=False, default=str, indent=2)
        return StreamingResponse(
            io.BytesIO(json_data.encode("utf-8")),
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=hr-report.json"
            },
        )

    # ------------------------------
    # 📤 CSV Export (Basisdaten + Audits)
    # ------------------------------
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # 👥 Mitarbeiter
    writer.writerow(["Employee ID", "Name", "Department", "Position", "Created"])
    for e in employees:
        writer.writerow([e.employee_id, e.name, e.department, e.position, e.created])

    # 🧾 HR Audit Logs
    buffer.write("\n\n--- HR AUDIT LOGS ---\n")
    writer.writerow(["ID", "User", "Role", "Action", "Resource", "Details", "Created At"])
    for a in hr_audits:
        writer.writerow([
            a.id,
            a.user_email,
            a.role,
            a.action,
            a.resource,
            a.details,
            a.created_at,
        ])

    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue().encode("utf-8")]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=hr-report.csv"
        },
    )
