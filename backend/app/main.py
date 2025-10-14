import os
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import register_routers
from .core.auth import get_current_user

# === FastAPI App ===
app = FastAPI(
    title="Workmate API",
    version="0.1.0",
    description="HR management system",
)

# === CORS ===
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://ui.workmate.test:5173",
    "https://ui.workmate.test",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Upload-Verzeichnisse sicherstellen ===
os.makedirs("app/uploads/avatar", exist_ok=True)

# === Static Files mounten ===
# Einheitliche URL-Struktur, egal ob lokal oder hinter Caddy:
# -> https://api.workmate.test/uploads/avatar/<file>.png
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

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
