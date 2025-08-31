# helpers.py
from typing import Optional
from fastapi import Request
import os, re

def sanitize_filename(name: Optional[str]) -> str:
    if not name:
        name = "upload"
    name = os.path.basename(name)
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)

def make_abs_upload_url(request: Request, file_url: Optional[str]) -> Optional[str]:
    if not file_url:
        return None
    if file_url.startswith(("http://", "https://")):
        return file_url

    # Normalisieren auf "app/uploads/<...>"
    path = file_url.lstrip("/")
    if path.startswith("uploads/"):
        path = "app/" + path                  # uploads/... -> app/uploads/...
    elif not path.startswith("app/uploads/"):
        path = f"app/uploads/{path}"          # nur Dateiname -> app/uploads/...

    rel = path[len("app/uploads/"):]          # Teil nach /app/uploads/
    return str(request.url_for("uploads", path=rel))  # -> /app/uploads/<rel>
