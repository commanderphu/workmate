import os
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import register_routers
from .core.auth import get_current_user
from .core.test_auth_middleware import TestAuthMiddleware

# ====== Basis Verzeichnis =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Immer diesen Pfad verwenden – kommt aus Compose
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
os.makedirs(os.path.join(UPLOAD_DIR, "documents"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "avatar"), exist_ok=True)


# === FastAPI App ===
app = FastAPI(
    title="Workmate API",
    version="0.1.0",
    description="HR management system",
)

# === CORS ===
origins = [
    # UI / Frontend
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://ui.workmate.test:5173",
    "https://ui.workmate.test",
    
    # API / Backend
    "https://api.workmate.test",
    "http://api.workmate.test",
    # Login / KeyCloak
    "https://login.workmate.test",
    "http://keycloak:8080/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TestAuthMiddleware)

# === Static Files mounten ===
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# === Router registrieren ===
register_routers(app)

# === System-Endpunkte ===
@app.get("/healthz", tags=["_infra"])
def healthz():
    return {"status": "ok"}

@app.get("/", tags=["_infra"])
def root():
    return {"message": "Workmate API. See /docs for OpenAPI."}

@app.get("/secure", tags=["auth"])
def secure(user=Depends(get_current_user)):
    return {
        "message": f"Hallo {user['preferred_username']}",
        "email": user.get("email"),
    }
