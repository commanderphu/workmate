from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/vacation-requests", tags=["Vacation Requests"])


@router.post("/", response_model=schemas.VacationRequestOut)
def create_vacation_request(payload: schemas.VacationRequestCreate, db: Session = Depends(get_db)):
    if not db.get(models.Employee, payload.employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    vr = models.VacationRequest(**payload.model_dump())
    db.add(vr)
    db.commit()
    db.refresh(vr)
    return vr


@router.get("/", response_model=list[schemas.VacationRequestOut])
def list_vacation_requests(
    db: Session = Depends(get_db),
    employee_id: Optional[UUID] = Query(None),
    status: Optional[models.VacationStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    stmt = select(models.VacationRequest)
    if employee_id:
        stmt = stmt.where(models.VacationRequest.employee_id == employee_id)
    if status:
        stmt = stmt.where(models.VacationRequest.status == status)

    stmt = stmt.order_by(models.VacationRequest.start_date.desc()).offset((page-1)*page_size).limit(page_size)
    return db.scalars(stmt).all()


@router.get("/{vr_id}", response_model=schemas.VacationRequestOut)
def get_vacation_request(vr_id: UUID, db: Session = Depends(get_db)):
    vr = db.get(models.VacationRequest, vr_id)
    if not vr:
        raise HTTPException(status_code=404, detail="VacationRequest not found")
    return vr


@router.put("/{vr_id}", response_model=schemas.VacationRequestOut)
def update_vacation_request(vr_id: UUID, payload: schemas.VacationRequestUpdate, db: Session = Depends(get_db)):
    vr = db.get(models.VacationRequest, vr_id)
    if not vr:
        raise HTTPException(status_code=404, detail="VacationRequest not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(vr, k, v)

    db.commit()
    db.refresh(vr)
    return vr


@router.delete("/{vr_id}", status_code=204)
def delete_vacation_request(vr_id: UUID, db: Session = Depends(get_db)):
    vr = db.get(models.VacationRequest, vr_id)
    if not vr:
        raise HTTPException(status_code=404, detail="VacationRequest not found")
    db.delete(vr)
    db.commit()
