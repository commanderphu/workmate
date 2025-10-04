from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.database import get_db
from app import models

router = APIRouter(prefix="/meta", tags=["Meta"])

@router.get("/departments")
def list_departments(db: Session = Depends(get_db)):
    rows = db.execute(
        select(models.Employee.department)
        .where(models.Employee.department.isnot(None))
        .group_by(models.Employee.department)
        .order_by(func.count().desc())
    ).all()
    # rows ist Liste von Tuples [(dept,), ...]
    return [r[0] for r in rows if r[0]]

@router.get("/roles")
def list_roles(db: Session = Depends(get_db)):
    # einfache Heuristik: distinct role aus Employee (falls vorhanden)
    if hasattr(models.Employee, "role"):
        rows = db.execute(
            select(models.Employee.role)
            .where(models.Employee.role.isnot(None))
            .group_by(models.Employee.role)
            .order_by(func.count().desc())
        ).all()
        return [r[0] for r in rows if r[0]]
    # fallback: feste Liste
    return [
        "CEO / Gründer / Visionär",
        "CTO / Marketing & Social Media",
        "Backoffice / Organisation",
        "Backoffice & Social Media",
        "Facility Managerin",
        "Technik / Hausmeister",
        "IT-Support",
        "Vertrieb",
        "Finanzen",
        "Consultant",
        "UX/UI Designerin",
        "Sicherheitsbeauftragter",
        "Support Juniorin",
        "Marketing-Assistentin / Azubi",
        "Azubi Backoffice",
    ]
