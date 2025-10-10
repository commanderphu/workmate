from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String, literal
from app.database import get_db
from datetime import datetime, timedelta, timezone, date
from app import models

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

def now_utc() -> datetime:
    # Vereinheitlicht: UTC im Backend, Frontend formatiert lokal
    n = datetime.now(timezone.utc)
    return n

@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    today = date.today()
    now = now_utc()
    next_7d_dt = now + timedelta(days=7)

    # Mitarbeiter gesamt
    total_employees = db.query(models.Employee).count()

    # Mitarbeiter je Department (für ein kleines Chart)
    per_dept = (
        db.query(models.Employee.department, func.count(models.Employee.id))
        .group_by(models.Employee.department)
        .all()
    )
    employees_by_department = {dept or "Unassigned": cnt for dept, cnt in per_dept}

    # Vacation Requests (pending)
    # Hinweis: Du nutzt weiter unten vr.status.value -> hier vergleichen wir wie gehabt mit String "pending"
    open_vacation_requests = (
        db.query(models.VacationRequest)
        .filter(models.VacationRequest.status == "pending")
        .count()
    )

    # Aktive Krankmeldungen (jetzt)
    active_sick_leaves = (
        db.query(models.SickLeave)
        .filter(
            models.SickLeave.start_date <= now,
            models.SickLeave.end_date >= now
        )
        .count()
    )

    # Laufende Zeitbuchungen (end_time ist NULL)
    active_time_entries = (
        db.query(models.TimeEntry)
        .filter(models.TimeEntry.end_time.is_(None))
        .count()
    )

    # Dokumente gesamt
    total_documents = db.query(models.Document).count()

    # Reminders
    pending_reminders = (
        db.query(models.Reminder)
        .filter(models.Reminder.status == "pending")
    )
    pending_total = pending_reminders.count()

    overdue = (
        pending_reminders
        .filter(
            models.Reminder.due_at.isnot(None),
            models.Reminder.due_at < now
        )
        .count()
    )

    due_next_7_days = (
        pending_reminders
        .filter(
            models.Reminder.due_at.isnot(None),
            models.Reminder.due_at >= now,
            models.Reminder.due_at <= next_7d_dt
        )
        .count()
    )

    return {
        "employees": {
            "total": total_employees,
            "by_department": employees_by_department,
        },
        "vacations": {
            "open_requests": open_vacation_requests,
        },
        "sick_leaves": {
            "active_now": active_sick_leaves,
        },
        "time_entries": {
            "active_now": active_time_entries,
        },
        "documents": {
            "total": total_documents,
        },
        "reminders": {
            "pending_total": pending_total,
            "overdue": overdue,
            "due_next_7_days": due_next_7_days,
        },
        "generated_at": now.isoformat(),
    }


@router.get("/employee/{employee_id}")
def get_employee_dashboard(employee_id: str, db: Session = Depends(get_db)):
    now = now_utc()
    today = date.today()
    next_60d = today + timedelta(days=60)

    # Employee anhand der Business-ID (KIT-xxxx) suchen
    emp = db.query(models.Employee).filter_by(employee_id=employee_id).first()
    if not emp:
        return {"error": f"Employee {employee_id} not found"}
    pk = emp.id  # interner PK für Joins

    # Dokumente pro Mitarbeiter
    total_documents = db.query(models.Document).filter_by(employee_id=pk).count()

    # Aktuelle Krankmeldung?
    current_sick_leave = db.query(models.SickLeave).filter(
        models.SickLeave.employee_id == pk,
        models.SickLeave.start_date <= now,
        models.SickLeave.end_date >= now
    ).first()

    # Offene Urlaubsanträge
    open_vacation_requests = db.query(models.VacationRequest).filter_by(
        employee_id=pk,
        status="pending"
    ).all()

    # Alle Urlaubsanträge
    all_vacation_requests = db.query(models.VacationRequest).filter_by(
        employee_id=pk
    ).all()

    # Nächste Urlaube (60 Tage)
    upcoming_vacations = db.query(models.VacationRequest).filter(
        models.VacationRequest.employee_id == pk,
        models.VacationRequest.start_date >= today,
        models.VacationRequest.start_date <= next_60d
    ).order_by(models.VacationRequest.start_date.asc()).all()

    # Laufende Zeitbuchung
    running_time_entry = db.query(models.TimeEntry).filter_by(
        employee_id=pk,
        end_time=None
    ).first()

    # Offene/überfällige Reminders
    employee_pending_reminders = (
        db.query(models.Reminder)
        .filter(
            models.Reminder.employee_id == pk,
            models.Reminder.status == "pending"
        )
        .order_by(models.Reminder.due_at.is_(None).asc(), models.Reminder.due_at.asc())
        .all()
    )
    overdue_count = (
        db.query(models.Reminder)
        .filter(
            models.Reminder.employee_id == pk,
            models.Reminder.status == "pending",
            models.Reminder.due_at.isnot(None),
            models.Reminder.due_at < now
        )
        .count()
    )

    return {
        "employee": {
            "id": emp.id,
            "employee_id": emp.employee_id,
            "name": emp.name,
            "department": emp.department,
        },
        "documents": {"total": total_documents},
        "sick_leave": {"active_now": current_sick_leave is not None},
        "vacations": {
            "open_requests": len(open_vacation_requests),
            "all_statuses": [vr.status.value if hasattr(vr.status, "value") else vr.status for vr in all_vacation_requests],
            "upcoming_60_days": [
                {"id": v.id, "start_date": str(v.start_date), "end_date": str(v.end_date)}
                for v in upcoming_vacations
            ],
        },
        "time_entries": {"running_start": running_time_entry.start_time if running_time_entry else None},
        "reminders": {
            "open": [{"id": r.id, "title": r.title, "due_at": r.due_at.isoformat() if r.due_at else None}
                     for r in employee_pending_reminders],
            "overdue_count": overdue_count,
        },
    }
    
@router.get("/reminders/top")
def top_employees_by_reminders(db: Session = Depends(get_db), limit: int = 5):
    results = (
        db.query(
            models.Employee.employee_id,
            models.Employee.name,
            func.count(models.Reminder.id).label("open_reminders")
        )
        .join(models.Reminder, models.Reminder.employee_id == models.Employee.id)
        .filter(models.Reminder.status == "pending")
        .group_by(models.Employee.id)
        .order_by(func.count(models.Reminder.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {"employee_id": r.employee_id, "name": r.name, "open_reminders": r.open_reminders}
        for r in results
    ]
from datetime import date, timedelta
from sqlalchemy import func

@router.get("/vacations/upcoming")
def upcoming_vacations(db: Session = Depends(get_db), days: int = 30, limit: int = 20):
    today = date.today()
    until = today + timedelta(days=days)

    # kommende Urlaube (Start liegt in den nächsten X Tagen)
    rows = (
        db.query(
            models.VacationRequest.id,
            models.VacationRequest.start_date,
            models.VacationRequest.end_date,
            models.VacationRequest.status,           # optional
            models.Employee.employee_id.label("employee_id"),
            models.Employee.name.label("name"),
        )
        .join(models.Employee, models.Employee.id == models.VacationRequest.employee_id)
        .filter(
            models.VacationRequest.start_date >= today,
            models.VacationRequest.start_date <= until,
        )
        .order_by(models.VacationRequest.start_date.asc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "employee_id": r.employee_id,
            "name": r.name,
            "start_date": str(r.start_date),
            "end_date": str(r.end_date),
            "status": r.status if isinstance(r.status, str) else getattr(r.status, "value", None),
        }
        for r in rows
    ]
@router.get("/absences/upcoming")
def upcoming_absences(db: Session = Depends(get_db), days: int = 30, limit: int = 20):
    today = date.today()
    until = today + timedelta(days=days)

    # Urlaubsanträge in den nächsten X Tagen
    vacations = (
        db.query(
            models.VacationRequest.id.label("id"),
            models.Employee.employee_id,
            models.Employee.name,
            models.VacationRequest.start_date,
            models.VacationRequest.end_date,
            func.coalesce(cast(models.VacationRequest.status, String), literal("approved")).label("status"),
        )
        .join(models.Employee, models.Employee.id == models.VacationRequest.employee_id)
        .filter(models.VacationRequest.start_date >= today,
                models.VacationRequest.start_date <= until)
        .all()
    )

    # Krankmeldungen: aktive und kommende
    sick = (
        db.query(
            models.SickLeave.id.label("id"),
            models.Employee.employee_id,
            models.Employee.name,
            models.SickLeave.start_date,
            models.SickLeave.end_date,
        )
        .join(models.Employee, models.Employee.id == models.SickLeave.employee_id)
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

    # sortiert nach Startdatum
    result.sort(key=lambda r: r["start_date"])
    return result[:limit]
