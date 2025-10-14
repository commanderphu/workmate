from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/time-entries", tags=["Time Entries"])


@router.post("/", response_model=schemas.TimeEntryOut)
def create_time_entry(payload: schemas.TimeEntryCreate, db: Session = Depends(get_db)):
    if not db.scalar(select(models.Employee).where(models.Employee.employee_id == payload.employee_id)):
        raise HTTPException(status_code=404, detail="Employee not found")

    te = models.TimeEntry(**payload.model_dump())
    db.add(te)
    db.commit()
    db.refresh(te)
    return te


@router.get("/", response_model=list[schemas.TimeEntryOut])
def list_time_entries(
    db: Session = Depends(get_db),
    employee_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    stmt = select(models.TimeEntry)
    if employee_id:
        stmt = stmt.where(models.TimeEntry.employee_id == employee_id)

    stmt = stmt.order_by(models.TimeEntry.start_time.desc()).offset((page - 1) * page_size).limit(page_size)
    return db.scalars(stmt).all()


@router.get("/{te_id}", response_model=schemas.TimeEntryOut)
def get_time_entry(te_id: str, db: Session = Depends(get_db)):
    te = db.get(models.TimeEntry, te_id)
    if not te:
        raise HTTPException(status_code=404, detail="TimeEntry not found")
    return te


@router.put("/{te_id}", response_model=schemas.TimeEntryOut)
def update_time_entry(te_id: str, payload: schemas.TimeEntryUpdate, db: Session = Depends(get_db)):
    te = db.get(models.TimeEntry, te_id)
    if not te:
        raise HTTPException(status_code=404, detail="TimeEntry not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(te, k, v)

    db.commit()
    db.refresh(te)
    return te


@router.delete("/{te_id}", status_code=204)
def delete_time_entry(te_id: str, db: Session = Depends(get_db)):
    te = db.get(models.TimeEntry, te_id)
    if not te:
        raise HTTPException(status_code=404, detail="TimeEntry not found")
    db.delete(te)
    db.commit()


# 🧩 By Business ID (KIT-ID)
@router.get("/by_business/{employee_id}", response_model=List[schemas.TimeEntryOut])
def list_te_by_business(employee_id: str, db: Session = Depends(get_db)):
    emp = db.scalar(select(models.Employee).where(models.Employee.employee_id == employee_id))
    if not emp:
        raise HTTPException(404, "Employee not found")

    return (
        db.query(models.TimeEntry)
        .filter(models.TimeEntry.employee_id == emp.employee_id)
        .order_by(models.TimeEntry.start_time.desc())
        .all()
    )


@router.post("/by_business/{employee_id}", response_model=schemas.TimeEntryOut, status_code=201)
def create_te_by_business(employee_id: str, payload: schemas.TimeEntryCreateIn, db: Session = Depends(get_db)):
    emp = db.scalar(select(models.Employee).where(models.Employee.employee_id == employee_id))
    if not emp:
        raise HTTPException(404, "Employee not found")

    te = models.TimeEntry(employee_id=emp.employee_id, **payload.model_dump())  # ✅ String
    db.add(te)
    db.commit()
    db.refresh(te)
    return te
