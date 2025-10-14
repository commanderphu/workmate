from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String, literal
from app.database import get_db
from datetime import datetime, timedelta, timezone, date
from app import models
from app.models import ReminderStatus, VacationRequest, VacationStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# ============================================================
# 🕒 Helper
# ============================================================

def now_utc() -> datetime:
    """Vereinheitlicht: UTC im Backend, Frontend formatiert lokal"""
    return datetime.now(timezone.utc)

# ============================================================
# 📊 Gesamtübersicht
# ============================================================

@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    now = now_utc()
    today = date.today()
    next_7d_dt = now + timedelta(days=7)

    total_employees = db.query(models.Employee).count()

    per_dept = (
        db.query(models.Employee.department, func.count(models.Employee.employee_id))
        .group_by(models.Employee.department)
        .all()
    )
    employees_by_department = {dept or "Unassigned": cnt for dept, cnt in per_dept}

    open_vacation_requests = (
        db.query(models.VacationRequest)
        .filter(models.VacationRequest.status == "pending")
        .count()
    )

    active_sick_leaves = (
        db.query(models.SickLeave)
        .filter(models.SickLeave.start_date <= now, models.SickLeave.end_date >= now)
        .count()
    )

    active_time_entries = (
        db.query(models.TimeEntry)
        .filter(models.TimeEntry.end_time.is_(None))
        .count()
    )

    total_documents = db.query(models.Document).count()

    pending_reminders = db.query(models.Reminder).filter(models.Reminder.status == "pending")
    pending_total = pending_reminders.count()
    overdue = pending_reminders.filter(
        models.Reminder.due_at.isnot(None), models.Reminder.due_at < now
    ).count()
    due_next_7_days = pending_reminders.filter(
        models.Reminder.due_at.isnot(None),
        models.Reminder.due_at >= now,
        models.Reminder.due_at <= next_7d_dt,
    ).count()

    return {
        "employees": {"total": total_employees, "by_department": employees_by_department},
        "vacations": {"open_requests": open_vacation_requests},
        "sick_leaves": {"active_now": active_sick_leaves},
        "time_entries": {"active_now": active_time_entries},
        "documents": {"total": total_documents},
        "reminders": {
            "pending_total": pending_total,
            "overdue": overdue,
            "due_next_7_days": due_next_7_days,
        },
        "generated_at": now.isoformat(),
    }

# ============================================================
# 👤 Mitarbeiter-Dashboard
# ============================================================

@router.get("/employee/{employee_id}")
def get_employee_dashboard(employee_id: str, db: Session = Depends(get_db)):
    now = now_utc()
    today = date.today()
    next_60d = today + timedelta(days=60)

    emp = db.query(models.Employee).filter_by(employee_id=employee_id).first()
    if not emp:
        return {"error": f"Employee {employee_id} not found"}

    # alle Relationen über die Business-ID!
    total_documents = db.query(models.Document).filter_by(employee_id=emp.employee_id).count()

    current_sick_leave = (
        db.query(models.SickLeave)
        .filter(
            models.SickLeave.employee_id == emp.employee_id,
            models.SickLeave.start_date <= now,
            models.SickLeave.end_date >= now,
        )
        .first()
    )

    open_vacation_requests = (
        db.query(models.VacationRequest)
        .filter_by(employee_id=emp.employee_id, status="pending")
        .all()
    )

    all_vacation_requests = (
        db.query(models.VacationRequest).filter_by(employee_id=emp.employee_id).all()
    )

    upcoming_vacations = (
        db.query(models.VacationRequest)
        .filter(
            models.VacationRequest.employee_id == emp.employee_id,
            models.VacationRequest.start_date >= today,
            models.VacationRequest.start_date <= next_60d,
        )
        .order_by(models.VacationRequest.start_date.asc())
        .all()
    )

    running_time_entry = (
        db.query(models.TimeEntry)
        .filter_by(employee_id=emp.employee_id, end_time=None)
        .first()
    )

    employee_pending_reminders = (
        db.query(models.Reminder)
        .filter(
            models.Reminder.employee_id == emp.employee_id,
            models.Reminder.status == "pending",
        )
        .order_by(models.Reminder.due_at.is_(None).asc(), models.Reminder.due_at.asc())
        .all()
    )

    overdue_count = (
        db.query(models.Reminder)
        .filter(
            models.Reminder.employee_id == emp.employee_id,
            models.Reminder.status == "pending",
            models.Reminder.due_at.isnot(None),
            models.Reminder.due_at < now,
        )
        .count()
    )

    return {
        "employee": {
            "id": str(emp.id),
            "employee_id": emp.employee_id,
            "name": emp.name,
            "department": emp.department,
            "email": emp.email,
            "position": emp.position,
        },
        "documents": {"total": total_documents},
        "sick_leave": {"active_now": current_sick_leave is not None},
        "vacations": {
            "open_requests": len(open_vacation_requests),
            "all_statuses": [
                vr.status.value if hasattr(vr.status, "value") else vr.status
                for vr in all_vacation_requests
            ],
            "upcoming_60_days": [
                {"id": v.id, "start_date": str(v.start_date), "end_date": str(v.end_date)}
                for v in upcoming_vacations
            ],
        },
        "time_entries": {
            "running_start": running_time_entry.start_time if running_time_entry else None
        },
        "reminders": {
            "open": [
                {
                    "id": r.id,
                    "title": r.title,
                    "due_at": r.due_at.isoformat() if r.due_at else None,
                }
                for r in employee_pending_reminders
            ],
            "overdue_count": overdue_count,
        },
    }

# ============================================================
# 🏆 Top Mitarbeiter nach offenen Remindern
# ============================================================


@router.get("/reminders/top")
def top_employees_by_reminders(db: Session = Depends(get_db), limit: int = 5):
    count_open = func.count(models.Reminder.id).label("open_reminders")

    results = (
        db.query(
            models.Employee.employee_id,
            models.Employee.name,
            count_open,
        )
        .join(models.Reminder, models.Reminder.employee_id == models.Employee.employee_id)
        .filter(models.Reminder.status == ReminderStatus.pending)
        .group_by(models.Employee.employee_id, models.Employee.name)
        .order_by(count_open.desc())
        .limit(limit)
        .all()
    )

    return [
        {"employee_id": r.employee_id, "name": r.name, "open_reminders": r.open_reminders}
        for r in results
    ]

@router.get("/vacations/upcoming")
def upcoming_vacations(db: Session = Depends(get_db), days: int = 30, limit: int = 20):
    today = date.today()
    until = today + timedelta(days=days)

    rows = (
        db.query(
            models.VacationRequest.id,
            models.VacationRequest.start_date,
            models.VacationRequest.end_date,
            models.VacationRequest.status,
            models.Employee.employee_id,
            models.Employee.name,
        )
        .join(models.Employee, models.Employee.employee_id == models.VacationRequest.employee_id)
        .filter(
            models.VacationRequest.start_date >= today,
            models.VacationRequest.start_date <= until,
        )
        .order_by(models.VacationRequest.start_date.asc().nulls_last())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "employee_id": r.employee_id,
            "name": r.name,
            "start_date": r.start_date.isoformat(),
            "end_date": r.end_date.isoformat(),
            "status": r.status.value if hasattr(r.status, "value") else r.status,
        }
        for r in rows
    ]

# ============================================================
# 🚑 Kommende Abwesenheiten (Urlaub + Krank)
# ============================================================

@router.get("/absences/upcoming")
def upcoming_absences(db: Session = Depends(get_db), days: int = 30, limit: int = 20):
    today = date.today()
    until = today + timedelta(days=days)

    vacations = (
        db.query(
            models.VacationRequest.id.label("id"),
            models.Employee.employee_id,
            models.Employee.name,
            models.VacationRequest.start_date,
            models.VacationRequest.end_date,
            func.coalesce(cast(models.VacationRequest.status, String), literal("approved")).label("status"),
        )
        .join(models.Employee, models.Employee.employee_id == models.VacationRequest.employee_id)
        .filter(models.VacationRequest.start_date >= today,
                models.VacationRequest.start_date <= until)
        .all()
    )

    sick = (
        db.query(
            models.SickLeave.id.label("id"),
            models.Employee.employee_id,
            models.Employee.name,
            models.SickLeave.start_date,
            models.SickLeave.end_date,
        )
        .join(models.Employee, models.Employee.employee_id == models.SickLeave.employee_id)
        .filter(models.SickLeave.end_date >= today)
        .all()
    )

    result = []
    for v in vacations:
        result.append({
            "id": f"vac_{v.id}",
            "employee_id": v.employee_id,
            "name": v.name,
            "type": "vacation",
            "status": v.status,
            "start_date": str(v.start_date),
            "end_date": str(v.end_date),
        })
    for s in sick:
        result.append({
            "id": f"sick_{s.id}",
            "employee_id": s.employee_id,
            "name": s.name,
            "type": "sick",
            "status": "sick",
            "start_date": str(s.start_date),
            "end_date": str(s.end_date),
        })

    result.sort(key=lambda r: r["start_date"])
    return result[:limit]
