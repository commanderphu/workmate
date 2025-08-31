from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import Column

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=List[schemas.EmployeeOut])
def get_employees(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Suche in name/email/employee_id/department/position"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    query = db.query(models.Employee)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (models.Employee.name.ilike(like)) |
            (models.Employee.email.ilike(like)) |
            (models.Employee.employee_id.ilike(like)) |
            (models.Employee.department.ilike(like)) |
            (models.Employee.position.ilike(like))
        )
    rows = query.order_by(models.Employee.name.asc()).offset(offset).limit(limit).all()
    return rows

@router.get("/{employee_id}", response_model=schemas.EmployeeOut)
def get_employee(employee_id: UUID, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.post("/", response_model=schemas.EmployeeOut)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    new_emp = models.Employee(
        id=uuid4(),  # <-- Model hat UUID(as_uuid=True), also UUID-Objekt, kein str
        **employee.dict(),
        created=datetime.utcnow(),
        updated=datetime.utcnow(),
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

@router.put("/{employee_id}", response_model=schemas.EmployeeOut)
def update_employee(employee_id: UUID, updated: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    payload = updated.dict(exclude_unset=True)
    for key, value in payload.items():
        setattr(emp, key, value)
    # Set the updated timestamp if 'updated' is a mapped attribute
    if hasattr(emp, "updated") and isinstance(getattr(type(emp), "updated", None), Column):
        emp.updated = datetime.utcnow()
    db.commit()
    db.refresh(emp)
    return emp
    return emp

@router.delete("/{employee_id}")
def delete_employee(employee_id: UUID, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
    return {"detail": "Employee deleted"}
