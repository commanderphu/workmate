from datetime import datetime, timezone
from typing import Optional, List
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


# ------------------------------------------------------------------
# 1) BUSINESS-ID ROUTES (müssen VOR den UUID-Routen stehen!)
# ------------------------------------------------------------------

@router.get("/by_business/{employee_id}", response_model=List[schemas.ReminderOut])
def list_reminders_by_business_id(employee_id: str, db: Session = Depends(get_db)):
    emp = (
        db.query(models.Employee)
        .filter(models.Employee.employee_id == employee_id)
        .first()
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    rows = (
        db.query(models.Reminder)
        .filter(models.Reminder.employee_id == emp.id)  # FK ist UUID
        .order_by(models.Reminder.due_at.asc().nulls_last(), models.Reminder.created.asc())
        .all()
    )
    return [add_is_overdue(r) for r in rows]


@router.post("/by_business/{employee_id}", response_model=schemas.ReminderOut, status_code=201)
def create_reminder_by_business_id(
    employee_id: str,
    payload: schemas.ReminderCreateIn,  # title, description?, due_at?, reminder_time?, status?, linked_to?
    db: Session = Depends(get_db),
):
    emp = (
        db.query(models.Employee)
        .filter(models.Employee.employee_id == employee_id)
        .first()
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    fields = {
        "title": payload.title.strip(),
        "description": (payload.description or "").strip() or None,
        "due_at": payload.due_at,
    }
    if hasattr(models.Reminder, "reminder_time"):
        fields["reminder_time"] = payload.reminder_time
    if hasattr(models.Reminder, "status"):
        fields["status"] = payload.status or "pending"
    if hasattr(models.Reminder, "linked_to"):
        fields["linked_to"] = payload.linked_to

    new_r = models.Reminder(
        employee_id=emp.id,
        **fields,
        created=datetime.utcnow(),
        updated=datetime.utcnow(),
    )
    db.add(new_r)
    db.commit()
    db.refresh(new_r)
    return add_is_overdue(new_r)


# ------------------------------------------------------------------
# 2) „Normale“ CRUD-Routen
# ------------------------------------------------------------------

@router.post("/", response_model=schemas.ReminderOut)
def create_reminder(payload: schemas.ReminderCreate, db: Session = Depends(get_db)):
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
        clauses.append(or_(models.Reminder.title.ilike(like), models.Reminder.description.ilike(like)))

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


# >>> HIER jetzt der UUID-Konverter! <<<
@router.get("/{reminder_id:uuid}", response_model=schemas.ReminderOut)
def get_reminder(reminder_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(models.Reminder, reminder_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return add_is_overdue(obj)


@router.patch("/{reminder_id:uuid}", response_model=schemas.ReminderOut)
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


@router.put("/{reminder_id:uuid}", response_model=schemas.ReminderOut)
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


@router.post("/{reminder_id:uuid}/done", response_model=schemas.ReminderOut)
def mark_done(reminder_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(models.Reminder, reminder_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reminder not found")
    obj.status = models.ReminderStatus.done
    db.commit()
    db.refresh(obj)
    return add_is_overdue(obj)


@router.delete("/{reminder_id:uuid}", status_code=204)
def delete_reminder(reminder_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(models.Reminder, reminder_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(obj)
    db.commit()
