from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/sick-leaves", tags=["Sick Leaves"])


# 🔹 Standard Create
@router.post("/", response_model=schemas.SickLeaveOut)
def create_sick_leave(payload: schemas.SickLeaveCreate, db: Session = Depends(get_db)):
    if not db.scalar(select(models.Employee).where(models.Employee.employee_id == payload.employee_id)):
        raise HTTPException(status_code=404, detail="Employee not found")
    if payload.document_id and not db.get(models.Document, payload.document_id):
        raise HTTPException(status_code=404, detail="Document not found")

    sl = models.SickLeave(**payload.model_dump())
    db.add(sl)
    db.commit()
    db.refresh(sl)
    return sl


# 🔹 List (optional Filter)
@router.get("/", response_model=list[schemas.SickLeaveOut])
def list_sick_leaves(
    db: Session = Depends(get_db),
    employee_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    stmt = select(models.SickLeave)
    if employee_id:
        stmt = stmt.where(models.SickLeave.employee_id == employee_id)
    stmt = stmt.order_by(models.SickLeave.start_date.desc()).offset((page - 1) * page_size).limit(page_size)
    return db.scalars(stmt).all()


# 🔹 Get by ID
@router.get("/{sl_id}", response_model=schemas.SickLeaveOut)
def get_sick_leave(sl_id: str, db: Session = Depends(get_db)):
    sl = db.get(models.SickLeave, sl_id)
    if not sl:
        raise HTTPException(status_code=404, detail="SickLeave not found")
    return sl


# 🔹 Update
@router.put("/{sl_id}", response_model=schemas.SickLeaveOut)
def update_sick_leave(sl_id: str, payload: schemas.SickLeaveUpdate, db: Session = Depends(get_db)):
    sl = db.get(models.SickLeave, sl_id)
    if not sl:
        raise HTTPException(status_code=404, detail="SickLeave not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(sl, k, v)

    db.commit()
    db.refresh(sl)
    return sl


# 🔹 Delete
@router.delete("/{sl_id}", status_code=204)
def delete_sick_leave(sl_id: str, db: Session = Depends(get_db)):
    sl = db.get(models.SickLeave, sl_id)
    if not sl:
        raise HTTPException(status_code=404, detail="SickLeave not found")
    db.delete(sl)
    db.commit()


# 🧩 By Business ID (KIT-xxxx)
@router.get("/by_business/{employee_id}", response_model=List[schemas.SickLeaveOut])
def list_sick_by_business(employee_id: str, db: Session = Depends(get_db)):
    emp = db.scalar(select(models.Employee).where(models.Employee.employee_id == employee_id))
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    return (
        db.query(models.SickLeave)
        .filter(models.SickLeave.employee_id == emp.employee_id)  # ✅ String-Vergleich
        .order_by(models.SickLeave.start_date.desc())
        .all()
    )


@router.post("/by_business/{employee_id}", response_model=schemas.SickLeaveOut, status_code=201)
def create_sick_by_business(employee_id: str, payload: schemas.SickLeaveCreateIn, db: Session = Depends(get_db)):
    emp = db.scalar(select(models.Employee).where(models.Employee.employee_id == employee_id))
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    if payload.document_id and not db.get(models.Document, payload.document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    if payload.end_date < payload.start_date:
        raise HTTPException(400, "end_date must be >= start_date")

    sl = models.SickLeave(employee_id=emp.employee_id, **payload.model_dump())  # ✅ String
    db.add(sl)
    db.commit()
    db.refresh(sl)
    return sl
