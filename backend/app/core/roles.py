from typing import Union, List, Callable, Awaitable
from fastapi import Depends, HTTPException, status
from functools import wraps
import inspect

from app.core.auth import get_current_user  # import anpassen, falls woanders

def require_roles(allowed_roles: Union[str, List[str]]):
    """
    Decorator, der prüft, ob der aktuelle Benutzer eine bestimmte Rolle oder Abteilung besitzt.
    Kann mit @require_roles("admin") oder @require_roles(["management", "admin"]) verwendet werden.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if user is None:
                raise HTTPException(status_code=500, detail="User dependency missing in route")

            role = user.get("department") if isinstance(user, dict) else getattr(user, "department", None)
            if role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: role '{role}' not in {allowed_roles}"
                )

            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator
