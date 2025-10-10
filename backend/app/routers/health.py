from datetime import datetime, timezone
import os
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/api", tags=["health"])

def _meta():
    return {
        "time": datetime.now(timezone.utc).isoformat(),
        "version": os.getenv("APP_VERSION", "unknown"),
        "git_sha": os.getenv("GIT_SHA", "unknown"),
    }

@router.get("/live", summary="Liveness probe")
def live():
    # App-Prozess läuft, keine externen Checks
    return {"status": "ok", "details": _meta()}

@router.get("/ready", summary="Readiness probe (DB required)")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "details": {"db": "ok", **_meta()}}
    except Exception as e:
        # 503 signalisiert: noch nicht bereit
        return Response(
            content={"status": "down", "details": {"db": f"error:{type(e).__name__}", **_meta()} }.__str__(),
            media_type="application/json",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

@router.get("/health", summary="Detailed health (DB + Meta)")
def health(db: Session = Depends(get_db)):
    status_flag = "ok"
    details = {"database": "ok", **_meta()}
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        status_flag = "degraded"
        details["database"] = f"error:{type(e).__name__}"
    return {"status": status_flag, "details": details}
