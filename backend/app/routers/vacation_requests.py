from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/vacation-requests", tags=["Vacation Requests"])


@router.post("/", response_model=schemas.VacationRequestOut)
def create_vacation_request(payload: schemas.VacationRequestCreate, db: Session = Depends(get_db)):
    if not db.scalar(select(models.Employee).where(models.Employee.employee_id == payload.employee_id)):
        raise HTTPException(status_code=404, detail="Employee not found")

    vr = models.VacationRequest(**payload.model_dump())
    db.add(vr)
    db.commit()
    db.refresh(vr)
    return vr


@router.get("/", response_model=list[schemas.VacationRequestOut])
def list_vacation_requests(
    db: Session = Depends(get_db),
    employee_id: Optional[str] = Query(None),
    status: Optional[models.VacationStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    stmt = select(models.VacationRequest)
    if employee_id:
        stmt = stmt.where(models.VacationRequest.employee_id == employee_id)
    if status:
        stmt = stmt.where(models.VacationRequest.status == status)

    stmt = stmt.order_by(models.VacationRequest.start_date.desc()).offset((page - 1) * page_size).limit(page_size)
    return db.scalars(stmt).all()


@router.get("/{vr_id}", response_model=schemas.VacationRequestOut)
def get_vacation_request(vr_id: str, db: Session = Depends(get_db)):
    vr = db.get(models.VacationRequest, vr_id)
    if not vr:
        raise HTTPException(status_code=404, detail="VacationRequest not found")
    return vr


@router.put("/{vr_id}", response_model=schemas.VacationRequestOut)
def update_vacation_request(vr_id: str, payload: schemas.VacationRequestUpdate, db: Session = Depends(get_db)):
    vr = db.get(models.VacationRequest, vr_id)
    if not vr:
        raise HTTPException(status_code=404, detail="VacationRequest not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(vr, k, v)

    db.commit()
    db.refresh(vr)
    return vr


@router.delete("/{vr_id}", status_code=204)
def delete_vacation_request(vr_id: str, db: Session = Depends(get_db)):
    vr = db.get(models.VacationRequest, vr_id)
    if not vr:
        raise HTTPException(status_code=404, detail="VacationRequest not found")
    db.delete(vr)
    db.commit()


# 🧩 By Business ID (KIT-ID)
@router.get("/by_business/{employee_id}", response_model=List[schemas.VacationRequestOut])
def list_vr_by_business(employee_id: str, db: Session = Depends(get_db)):
    emp = db.scalar(select(models.Employee).where(models.Employee.employee_id == employee_id))
    if not emp:
        raise HTTPException(404, "Employee not found")

    return (
        db.query(models.VacationRequest)
        .filter(models.VacationRequest.employee_id == emp.employee_id)
        .order_by(models.VacationRequest.start_date.desc())
        .all()
    )


@router.post("/by_business/{employee_id}", response_model=schemas.VacationRequestOut, status_code=201)
def create_vr_by_business(employee_id: str, payload: schemas.VacationRequestCreateIn, db: Session = Depends(get_db)):
    emp = db.scalar(select(models.Employee).where(models.Employee.employee_id == employee_id))
    if not emp:
        raise HTTPException(404, "Employee not found")

    if payload.end_date < payload.start_date:
        raise HTTPException(400, "end_date must be >= start_date")

    vr = models.VacationRequest(employee_id=emp.employee_id, **payload.model_dump())  # ✅ String
    db.add(vr)
    db.commit()
    db.refresh(vr)
    return vr
