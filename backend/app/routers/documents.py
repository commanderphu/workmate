from uuid import UUID, uuid4
from typing import Optional,List
from datetime import datetime
import os
import shutil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session,joinedload
from sqlalchemy import select, and_, or_

from app import models, schemas
from app.database import get_db
from app.enums import DocumentStatus, DocumentType
from app.core.auth import get_current_user
from app.core.audit import log_action
from app.core.roles import require_roles

from pathlib import Path
import os

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
UPLOAD_ROOT = UPLOAD_DIR / "documents"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

BACKEND_URL = os.getenv("BACKEND_URL", "https://api.workmate.test")

router = APIRouter(prefix="/documents", tags=["Documents"])


# ============================================================
# 🔧 Hilfsfunktion
# ============================================================

def resolve_employee(db: Session, identifier: str):
    """
    Gibt den Employee anhand seiner internen UUID oder Business-ID (KIT-xxxx) zurück.
    """
    if not identifier:
        return None
    try:
        return db.get(models.Employee, UUID(identifier))
    except (ValueError, TypeError):
        return db.scalar(
            select(models.Employee).where(models.Employee.employee_id == identifier)
        )


# ============================================================
#  TYPES
# ============================================================

@router.get("/types", response_model=list[str])
def list_document_types():
    """Gibt alle erlaubten DocumentType-ENUM-Werte zurück."""
    return [e.value for e in DocumentType]

# ============================================================
# 🧩 CRUD Endpoints
# ============================================================

@router.put("/{doc_id}", response_model=schemas.DocumentOut)
@require_roles(["management", "admin"])
async def approve_document(doc_id: UUID, payload: schemas.DocumentUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    doc = db.get(models.Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if payload.status is not None:
        # Prüfen, ob schon ein Enum oder ein String übergeben wurde
        if isinstance(payload.status, str):
            try:
                doc.status = DocumentStatus(payload.status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Ungültiger Dokumentstatus: {payload.status}")
        else:
            doc.status = payload.status
    db.commit()
    db.refresh(doc)

    # 🧾 Audit-Eintrag
    log_action(db, user, "approve", f"document:{doc_id}", f"status → {payload.status}")

    return doc


from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, or_
from typing import Optional, List
from app import models, schemas
from app.database import get_db
from app.enums import DocumentStatus, DocumentType

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/", response_model=List[schemas.DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    employee_id: Optional[str] = Query(None, description="KIT-ID oder UUID des Mitarbeiters"),
    status: Optional[DocumentStatus] = Query(None),
    doc_type: Optional[DocumentType] = Query(None),
    q: Optional[str] = Query(None, description="Suche in Titel/Notizen"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    """Listet alle Dokumente inkl. Mitarbeitername & KIT-ID."""
    stmt = (
        select(models.Document)
        .options(joinedload(models.Document.employee))
        .order_by(models.Document.upload_date.desc().nulls_last())
    )

    filters = []

    # 🔹 Filter
    if employee_id:
        emp = (
            db.query(models.Employee)
            .filter(models.Employee.employee_id == employee_id)
            .first()
        )
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")
        filters.append(models.Document.employee_id == emp.employee_id)

    if status:
        filters.append(models.Document.status == status)
    if doc_type:
        filters.append(models.Document.document_type == doc_type)
    if q:
        like = f"%{q}%"
        filters.append(or_(
            models.Document.title.ilike(like),
            models.Document.notes.ilike(like)
        ))

    if filters:
        stmt = stmt.where(and_(*filters))

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    docs = db.scalars(stmt).all()

    # 🧠 Saubere Response mit Mapping
    result = []
    for d in docs:
        result.append({
            "id": str(d.id),
            "title": d.title,
            "document_type": d.document_type,
            "status": d.status,
            "file_url": d.file_url,
            "is_original_required": d.is_original_required,
            "upload_date": d.upload_date,
            "notes": d.notes,
            "employee_id": d.employee_id,
            "employee_name": getattr(d.employee, "name", None),
            "employee_business_id": getattr(d.employee, "employee_id", None),
        })
    return result


@router.get("/{doc_id}", response_model=schemas.DocumentOut)
def get_document(doc_id: UUID, db: Session = Depends(get_db)):
    """Lädt ein einzelnes Dokument anhand seiner internen UUID."""
    doc = db.get(models.Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{doc_id}", response_model=schemas.DocumentOut)
def update_document(
    doc_id: UUID,
    payload: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    doc = db.get(models.Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 🧩 Mitarbeiter darf nur eigene bearbeiten
    if user["role"] not in ("backoffice", "management") and doc.employee_id != user["employee_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to modify this document")

    # 🧾 Nur HR oder Management dürfen Status ändern
    data = payload.model_dump(exclude_unset=True)

# 👤 Mitarbeiter darf Status/Kommentar nicht ändern
    if user["role"] not in ("backoffice", "management"):
        data["status"] = doc.status
        data["comment"] = doc.comment

    for key, value in data.items():
        setattr(doc, key, value)

    db.commit()
    db.refresh(doc)
    return doc



@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: UUID, db: Session = Depends(get_db)):
    """Löscht ein Dokument (inkl. Datei, falls vorhanden)."""
    doc = db.get(models.Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.file_url:
        path = os.path.join("app", doc.file_url.lstrip("/"))
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"⚠️ Datei konnte nicht gelöscht werden: {e}")

    db.delete(doc)
    db.commit()


# ============================================================
# 📤 Datei-Upload
# ============================================================

@router.post("/upload/{employee_id}", response_model=schemas.DocumentOut)
async def upload_document(employee_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    employee = resolve_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")

    emp_dir = UPLOAD_ROOT / str(employee.employee_id)
    emp_dir.mkdir(parents=True, exist_ok=True)

    name, ext = os.path.splitext(file.filename or "unnamed")
    safe_name = f"{uuid4().hex}{ext}"
    save_path = emp_dir / safe_name

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"{BACKEND_URL}/uploads/documents/{employee.employee_id}/{safe_name}"

    doc = models.Document(
        employee_id=employee.employee_id,
        title=name,
        file_url=file_url,
        upload_date=datetime.utcnow(),
        status=DocumentStatus.pending,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/download/{employee_id}/{filename}")
def download_document(employee_id: str, filename: str):
    file_path = UPLOAD_ROOT / employee_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path), filename=filename)
