# app/routers/hr.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user   # liefert den User (Keycloak)
from app.core.roles import require_roles     # dein Decorator (mit Aliases)
from app.services import hr_service    
from app.schemas import HROverview     # nutzt dashboard.overview intern

router = APIRouter(prefix="/hr", tags=["HR"])

@router.get("/overview", response_model=HROverview)
@require_roles(["management", "hr"])   # Backoffice zählt als HR (per Alias)
async def hr_overview(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),     # wichtig: damit der Decorator 'user' sieht
):
    """
    Liefert HR-KPIs als Subset der Dashboard-Aggregation.
    Quelle: dashboard.overview → hr_service.filter()
    """
    print(f"[HR] Overview called by {user.get('email')}")
    return hr_service.get_hr_overview(db)

@router.get("/stats/departments")
@require_roles(["management", "hr"])
async def hr_stats_departments(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    data = hr_service.get_hr_overview(db)
    return data["departments"]  # Liste: [{department, count}]
