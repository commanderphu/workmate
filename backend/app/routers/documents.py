# app/routers/documents.py
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime
import os
import shutil
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Form,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, or_

from app import models, schemas
from app.database import get_db
from app.enums import DocumentStatus, DocumentType
from app.core.auth import get_current_user
from app.core.audit import log_action
from app.core.roles import require_roles


# ============================================================
# 📁 Upload-Verzeichnisse
# ============================================================

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
UPLOAD_ROOT = UPLOAD_DIR / "documents"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

BACKEND_URL = os.getenv("BACKEND_URL", "https://api.workmate.test")

router = APIRouter(prefix="/documents", tags=["Documents"])


# ============================================================
# 🔧 Hilfsfunktion
# ============================================================

def resolve_employee(db: Session, identifier: str):
    """Sucht einen Mitarbeiter anhand seiner KIT-ID (z. B. 'KIT-0001')."""
    if not identifier:
        return None
    return db.scalar(
        select(models.Employee).where(models.Employee.employee_id == identifier)
    )


# ============================================================
# 📄 Document Types
# ============================================================

@router.get("/types", response_model=list[str])
def list_document_types():
    """Gibt alle erlaubten DocumentType-ENUM-Werte zurück."""
    return [e.value for e in DocumentType]


# ============================================================
# 📋 Liste / Filter
# ============================================================

@router.get("/", response_model=List[schemas.DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    employee_id: Optional[str] = Query(None, description="KIT-ID des Mitarbeiters"),
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

    # 🔹 Nach Mitarbeiter filtern (KIT-ID)
    if employee_id:
        emp = resolve_employee(db, employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")
        filters.append(models.Document.employee_id == emp.employee_id)

    # 🔹 Nach Status / Typ / Text
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

    for f in filters:
        stmt = stmt.where(f)

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    docs = db.scalars(stmt).all()

    return [
        {
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
        }
        for d in docs
    ]


# ============================================================
# ✏️ Update / Approve
# ============================================================

@router.put("/{doc_id}", response_model=schemas.DocumentOut)
def update_document(
    doc_id: UUID,
    payload: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Aktualisiert ein Dokument (z. B. Notizen, Typ, Status)."""
    doc = db.get(models.Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 🔒 Berechtigung prüfen
    if user["role"] not in ("backoffice", "management") and doc.employee_id != user["employee_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    data = payload.model_dump(exclude_unset=True)

    # Nur HR/Management dürfen Status/Kommentar ändern
    if user["role"] not in ("backoffice", "management"):
        data["status"] = doc.status
        data["comment"] = getattr(doc, "comment", None)

    for key, value in data.items():
        setattr(doc, key, value)

    # 🧾 Audit vor dem Commit hinzufügen (gleiche Transaktion)
    log_action(db, user, "update", f"document:{doc_id}", data)

    db.commit()
    db.refresh(doc)
    print(f"✅ Dokument aktualisiert & Audit gespeichert: {doc_id}")
    return doc


# ============================================================
# 🗑️ Delete
# ============================================================

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Löscht ein Dokument (inkl. Datei)."""
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
    log_action(db, user, "delete", f"document:{doc_id}", "Dokument gelöscht")

    db.commit()
    print(f"✅ Dokument gelöscht & Audit gespeichert: {doc_id}")


# ============================================================
# 📤 Upload
# ============================================================

@router.post("/upload/{employee_id}", response_model=schemas.DocumentOut)
async def upload_document(
    employee_id: str,
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    notes: Optional[str] = Form(None),
    is_original_required: bool = Form(False),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Speichert neues Dokument mit Metadaten für Mitarbeiter."""
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
        document_type=document_type,
        file_url=file_url,
        notes=notes,
        is_original_required=is_original_required,
        upload_date=datetime.utcnow(),
        status=DocumentStatus.pending,
    )

    db.add(doc)
    db.flush()  # ⚡ ID wird generiert, bevor Audit geschrieben wird

    log_action(db, user, "upload", f"document:{doc.id}", {
        "filename": name,
        "type": document_type,
        "employee_id": employee.employee_id,
    })

    db.commit()
    db.refresh(doc)
    print(f"✅ Upload abgeschlossen & Audit gespeichert: {doc.id}")
    return doc


# ============================================================
# 📥 Download
# ============================================================

@router.get("/download/{employee_id}/{filename}")
def download_document(
    employee_id: str,
    filename: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Gibt eine hochgeladene Datei zurück."""
    file_path = UPLOAD_ROOT / employee_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # 🧾 Optionales Logging für Nachvollziehbarkeit
    log_action(db, user, "download", f"document:{filename}", {"employee_id": employee_id})
    db.commit()

    return FileResponse(str(file_path), filename=filename)
