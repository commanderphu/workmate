from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import Column, func
from sqlalchemy.exc import IntegrityError


from app import models, schemas
from app.database import get_db
from app.core.auth import get_current_user


router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/me", response_model=schemas.EmployeeOut)
def get_me(current_user: models.Employee = Depends(get_current_user)):
    return current_user


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
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user),
):
    """🧩 Legt einen neuen Mitarbeiter-Eintrag an, wenn der User noch keinen hat."""

    # 🔐 Schutz: User darf nur sein eigenes Profil anlegen
    if employee.email != current_user.email:
        raise HTTPException(status_code=403, detail="You can only create your own profile")

    # 🔢 Nächste freie Business-ID bestimmen
    last_emp = (
        db.query(models.Employee)
        .filter(models.Employee.employee_id.like("KIT-%"))
        .order_by(models.Employee.employee_id.desc())
        .first()
    )

    if last_emp and last_emp.employee_id.startswith("KIT-"):
        try:
            next_num = int(last_emp.employee_id.split("-")[1]) + 1
        except ValueError:
            next_num = 1
    else:
        next_num = 1

    next_id = f"KIT-{next_num:04d}"

    # 🧱 Neues Employee-Objekt anlegen
    new_emp = models.Employee(
        id=uuid4(),
        employee_id=next_id,
        name=employee.name,
        email=employee.email,
        department=employee.department,
        position=employee.position,
        created=datetime.utcnow(),
        updated=datetime.utcnow(),
    )

    try:
        db.add(new_emp)
        db.commit()
        db.refresh(new_emp)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or employee_id already in use")

    return new_emp


@router.put("/{employee_id}", response_model=schemas.EmployeeOut)
def update_employee(employee_id: UUID, updated: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    payload = updated.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(emp, key, value)
    # Set the updated timestamp if 'updated' is a mapped attribute
    if hasattr(emp, "updated") and isinstance(getattr(type(emp), "updated", None), Column):
        emp.updated = datetime.utcnow()
    db.commit()
    db.refresh(emp)
    return emp

@router.delete("/{employee_id}")
def delete_employee(employee_id: UUID, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
    return {"detail": "Employee deleted"}

@router.put("/by_business/{employee_id}", response_model=schemas.EmployeeOut)
def update_employee_by_business_id(
    employee_id: str,
    payload: schemas.EmployeeUpdateIn,
    db: Session = Depends(get_db),
):
    emp = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    data = payload.model_dump(exclude_unset=True)

    # 1) Vorab-Check: E-Mail schon bei anderem Datensatz vergeben?
    new_email = data.get("email")
    if new_email:
        exists = (
            db.query(models.Employee.id)
              .filter(models.Employee.email == new_email, models.Employee.id != emp.id)
              .first()
        )
        if exists:
            raise HTTPException(status_code=409, detail="Email already in use")

    # 2) Felder setzen
    for k, v in data.items():
        setattr(emp, k, v)

    if hasattr(emp, "updated"):
        emp.updated = datetime.utcnow()

    try:
        db.add(emp)
        db.commit()
        db.refresh(emp)
    except IntegrityError as e:
        db.rollback()
        # Falls doch ein anderer Unique-Fehler kommt (z.B. employee_id)
        raise HTTPException(status_code=409, detail="Unique constraint violation") from e

    return emp
