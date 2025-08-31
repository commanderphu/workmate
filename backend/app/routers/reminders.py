from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/reminders", tags=["Reminders"])


def _to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def add_is_overdue(obj: models.Reminder) -> schemas.ReminderOut:
    due = _to_utc(obj.due_at)
    now = datetime.now(timezone.utc)
    is_overdue = bool(due and obj.status == models.ReminderStatus.pending and due < now)

    out = schemas.ReminderOut.model_validate(obj, from_attributes=True)
    return out.model_copy(update={"is_overdue": is_overdue})


@router.post("/", response_model=schemas.ReminderOut)
def create_reminder(payload: schemas.ReminderCreate, db: Session = Depends(get_db)):
    # existiert employee?
    if not db.get(models.Employee, payload.employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    item = models.Reminder(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return add_is_overdue(item)


@router.get("/", response_model=list[schemas.ReminderOut])
def list_reminders(
    db: Session = Depends(get_db),
    employee_id: Optional[UUID] = Query(None),
    status: Optional[models.ReminderStatus] = Query(None),
    due_before: Optional[datetime] = Query(None),
    due_after: Optional[datetime] = Query(None),
    q: Optional[str] = Query(None, description="Suche in title/description"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    clauses = []
    if employee_id:
        clauses.append(models.Reminder.employee_id == employee_id)
    if status:
        clauses.append(models.Reminder.status == status)
    if due_before:
        clauses.append(models.Reminder.due_at.is_not(None))
        clauses.append(models.Reminder.due_at <= _to_utc(due_before))
    if due_after:
        clauses.append(models.Reminder.due_at.is_not(None))
        clauses.append(models.Reminder.due_at >= _to_utc(due_after))
    if q:
        like = f"%{q}%"
        clauses.append(
            or_(
                models.Reminder.title.ilike(like),
                models.Reminder.description.ilike(like),
            )
        )

    stmt = select(models.Reminder)
    if clauses:
        stmt = stmt.where(and_(*clauses))

    stmt = (
        stmt.order_by(models.Reminder.due_at.nulls_last(), models.Reminder.created.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    rows = db.scalars(stmt).all()
    return [add_is_overdue(r) for r in rows]


@router.get("/{reminder_id}", response_model=schemas.ReminderOut)
def get_reminder(reminder_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(models.Reminder, reminder_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return add_is_overdue(obj)


# PATCH – Teilupdate
@router.patch("/{reminder_id}", response_model=schemas.ReminderOut)
def update_reminder(reminder_id: UUID, payload: schemas.ReminderUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Reminder, reminder_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reminder not found")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] not in (models.ReminderStatus.pending, models.ReminderStatus.done):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    for k, v in data.items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return add_is_overdue(obj)


# PUT – falls du PUT bevorzugst (Teilupdate via exclude_unset)
@router.put("/{reminder_id}", response_model=schemas.ReminderOut)
def put_reminder(reminder_id: UUID, payload: schemas.ReminderUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Reminder, reminder_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reminder not found")

    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] not in (models.ReminderStatus.pending, models.ReminderStatus.done):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    for k, v in data.items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return add_is_overdue(obj)


@router.post("/{reminder_id}/done", response_model=schemas.ReminderOut)
def mark_done(reminder_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(models.Reminder, reminder_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reminder not found")
    obj.status = models.ReminderStatus.done
    db.commit()
    db.refresh(obj)
    return add_is_overdue(obj)


@router.delete("/{reminder_id}", status_code=204)
def delete_reminder(reminder_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(models.Reminder, reminder_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(obj)
    db.commit()
