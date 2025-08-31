from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from datetime import datetime,date
from app import models

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    today = date.today()
    now = datetime.now()

    total_employees = db.query(models.Employee).count()
    open_vacation_requests = db.query(models.VacationRequest).filter(models.VacationRequest.status == "pending").count()
    active_sick_leaves = db.query(models.SickLeave).filter(
        models.SickLeave.start_date <= now,
        models.SickLeave.end_date >= now
        ).count()
    active_time_entries = db.query(models.TimeEntry).filter(
        models.TimeEntry.end_time.is_(None)
        ).count()
    total_documents = db.query(models.Document).count()

    return {
        "total_employees": total_employees,
        "open_vacation_requests": open_vacation_requests,
        "active_sick_leaves": active_sick_leaves,
        "active_time_entries": active_time_entries,
        "total_documents": total_documents,
    }


@router.get("/employee/{employee_id}")
def get_employee_dashboard(employee_id: str, db: Session = Depends(get_db)):
    now = datetime.now()

    total_documents = db.query(models.Document).filter_by(employee_id=employee_id).count()

    current_sick_leave = db.query(models.SickLeave).filter(
        models.SickLeave.employee_id == employee_id,
        models.SickLeave.start_date <= now,
        models.SickLeave.end_date >= now
    ).first()

    open_vacation_requests = db.query(models.VacationRequest).filter_by(
        employee_id=employee_id,
        status="pending"
    ).all()

    all_vacation_requests = db.query(models.VacationRequest).filter_by(
        employee_id=employee_id
    ).all()

    running_time_entry = db.query(models.TimeEntry).filter_by(
        employee_id=employee_id,
        end_time=None
    ).first()

    return {
        "total_documents": total_documents,
        "current_sick_leave": current_sick_leave is not None,
        "open_vacation_requests": len(open_vacation_requests),
        "vacation_requests": [vr.status.value for vr in all_vacation_requests],
        "running_time_entry": running_time_entry.start_time if running_time_entry else None
    }

