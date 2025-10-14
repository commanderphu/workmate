# app/core/auth.py
import requests
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from jwt.algorithms import RSAAlgorithm
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app import models

KEYCLOAK_INTERNAL = "http://keycloak:8080"
OIDC_ISSUER = "https://login.workmate.test/realms/kit"
CLIENT_ID = "workmate-ui"
JWKS_URI = f"{KEYCLOAK_INTERNAL}/realms/kit/protocol/openid-connect/certs"

auth_scheme = HTTPBearer()
_JWKS_CACHE = None


def get_jwks():
    global _JWKS_CACHE
    if _JWKS_CACHE:
        return _JWKS_CACHE
    try:
        res = requests.get(JWKS_URI, timeout=5)
        res.raise_for_status()
        jwks = res.json()
        _JWKS_CACHE = {key["kid"]: key for key in jwks["keys"]}
        return _JWKS_CACHE
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der JWKS: {e}")


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
):
    token = creds.credentials
    try:
        header = jwt.get_unverified_header(token)
        keys = get_jwks()
        key_data = keys.get(header.get("kid"))
        if not key_data:
            raise HTTPException(status_code=401, detail="Unknown key ID in token header")

        public_key = RSAAlgorithm.from_jwk(key_data)
        decoded = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
            issuer=OIDC_ISSUER,
        )

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")

    # --- User in DB finden
    email = decoded.get("email")
    username = decoded.get("preferred_username")
    user = None

    if email:
        user = db.scalar(select(models.Employee).where(models.Employee.email == email))
    if not user and username:
        user = db.scalar(select(models.Employee).where(
            (models.Employee.name.ilike(username)) |
            (models.Employee.employee_id.ilike(f"%{username}%"))
        ))

    if not user:
        raise HTTPException(status_code=404, detail="Kein Employee für aktuellen Benutzer gefunden")

    # --- Rolle ableiten aus Department
    dept = (user.department or "").lower()
    if dept in ("backoffice", "hr"):
        role = "backoffice"
    elif dept == "management":
        role = "management"
    else:
        role = "employee"

    result = {
        "preferred_username": user.name,
        "email": user.email,
        "employee_id": user.employee_id,
        "department": dept,
        "role": role,  # 🔹 Wichtig: vereinheitlichte Rolle für alle Checks
    }

    print("✅ Authenticated as:", result)
    return result




def require_roles(*allowed_roles: str):
    def wrapper(user = Depends(get_current_user)):
        role = user.get("role")
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return user
    return wrapper