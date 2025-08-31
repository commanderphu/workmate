from uuid import UUID
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/", response_model=schemas.DocumentOut)
def create_document(payload: schemas.DocumentCreate, db: Session = Depends(get_db)):
    if not db.get(models.Employee, payload.employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    doc = models.Document(**payload.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/", response_model=list[schemas.DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    employee_id: Optional[UUID] = Query(None),
    status: Optional[models.DocumentStatus] = Query(None),
    doc_type: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Suche in title/notes"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    stmt = select(models.Document)
    clauses = []
    if employee_id:
        clauses.append(models.Document.employee_id == employee_id)
    if status:
        clauses.append(models.Document.status == status)
    if doc_type:
        clauses.append(models.Document.document_type == doc_type)
    if q:
        like = f"%{q}%"
        clauses.append(or_(models.Document.title.ilike(like), models.Document.notes.ilike(like)))

    if clauses:
        stmt = stmt.where(and_(*clauses))

    stmt = stmt.order_by(models.Document.upload_date.desc().nulls_last()).offset((page-1)*page_size).limit(page_size)
    return db.scalars(stmt).all()


@router.get("/{doc_id}", response_model=schemas.DocumentOut)
def get_document(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(models.Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{doc_id}", response_model=schemas.DocumentOut)
def update_document(doc_id: UUID, payload: schemas.DocumentUpdate, db: Session = Depends(get_db)):
    doc = db.get(models.Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(doc, k, v)

    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(models.Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
