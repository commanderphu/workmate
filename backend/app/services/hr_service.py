# app/services/hr_service.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict
from sqlalchemy.orm import Session

from app.routers.dashboard import get_dashboard_overview  # ⚙️ bereits vorhanden
# -> deine Funktion dort heißt vermutlich get_dashboard_overview()

def get_hr_overview(db: Session):
    data = get_dashboard_overview(db)
    # extrahiere HR-relevante Keys
    return {
        "employees_total": data["employees"]["total"],
        "departments": [
            {"department": dept, "count": count}
            for dept, count in data["employees"]["by_department"].items()
        ],
        "open_vacations": data["vacations"]["open_requests"],
        "active_sick_leaves": data["sick_leaves"]["active_now"],
        "documents_total": data["documents"]["total"],
        "reminders_pending": data["reminders"]["pending_total"],
        "reminders_overdue": data["reminders"]["overdue"],
        "generated_at": data["generated_at"],
    }