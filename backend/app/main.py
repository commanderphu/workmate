from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware
from .routers import register_routers

app = FastAPI(title="Workmate API", version="0.1.0", description="HR management system")

origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/app/uploads", StaticFiles(directory="app/uploads"), name="uploads")
Base.metadata.create_all(bind=engine)

register_routers(app)

@app.get ("/healthz", tags=["_infra"])
def healthz():
    return {"status": "ok"}

@app.get("/", tags=["_infra"])
def root():
    return {"message": "Workmate API. See /docs for OpenAPI."}
