from fastapi import APIRouter, FastAPI

from . import documents, employees, sick_leaves, time_entries, vacation_requests, reminders, dashboard, meta, health, admin, hr

api_router = APIRouter()
api_router.include_router(documents.router)
api_router.include_router(employees.router)
api_router.include_router(sick_leaves.router)
api_router.include_router(time_entries.router)
api_router.include_router(vacation_requests.router)
api_router.include_router(reminders.router)
api_router.include_router(dashboard.router)
api_router.include_router(meta.router)
api_router.include_router(health.router)
api_router.include_router(admin.router)
api_router.include_router(hr.router)


def register_routers(app: FastAPI, api_prefix: str="") -> None:
    if api_prefix:
        app.include_router(api_router, prefix=api_prefix)
    else:
        app.include_router(api_router)