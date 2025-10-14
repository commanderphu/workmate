from datetime import datetime
from sqlalchemy.orm import Session
from app import models

def log_action(db: Session, user: dict, action: str, resource: str, details: str = ""):
    """Speichert eine Audit-Zeile in der DB."""
    try:
        log = models.AuditLog(
            user_email=user.get("email"),
            role=user.get("role"),
            action=action,
            resource=resource,
            details=details,
            created_at=datetime.utcnow(),
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"⚠️ Audit-Log konnte nicht geschrieben werden: {e}")
