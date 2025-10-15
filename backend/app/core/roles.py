# app/core/roles.py
from typing import Union, List, Callable
from fastapi import Depends, HTTPException, status
from functools import wraps
import inspect

from app.core.auth import get_current_user  # <- bei dir evtl. aus core/auth_utils o.ä.

# 🔁 Rollen-Aliases
ROLE_ALIASES = {
    "backoffice": "hr",
    "hr": "hr",
    "management": "management",
    "admin": "management",
    "support": "admin",
}

def normalize_role(role: str) -> str:
    """Wandelt z.B. 'backoffice' → 'hr' um"""
    return ROLE_ALIASES.get(role.lower(), role.lower())


def require_roles(allowed_roles: Union[str, List[str]]):
    """
    Decorator zur Rollenprüfung.
    Unterstützt Sync + Async Funktionen.
    Erwartet, dass der Route ein 'user' via Depends(get_current_user) übergeben wird.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    allowed_normalized = {normalize_role(r) for r in allowed_roles}

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # User aus Route holen
            user = kwargs.get("user")
            if user is None:
                raise HTTPException(
                    status_code=500,
                    detail="Missing 'user' in route — please include user: dict = Depends(get_current_user)",
                )

            # Rolle aus Abteilung oder Keycloak-Rollen bestimmen
            if isinstance(user, dict):
                role = user.get("department") or user.get("role")
                keycloak_roles = set(user.get("roles", []))
            else:
                role = getattr(user, "department", None)
                keycloak_roles = set(getattr(user, "roles", []))

            normalized_user_role = normalize_role(role) if role else None
            normalized_user_roles = {normalize_role(r) for r in keycloak_roles}

            # Zugriff prüfen
            if not (
                normalized_user_role in allowed_normalized
                or allowed_normalized.intersection(normalized_user_roles)
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Allowed: {allowed_normalized} | Your roles: {normalized_user_roles or normalized_user_role}",
                )

            # Call original route (sync oder async)
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
