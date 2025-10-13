import requests
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from jwt.algorithms import RSAAlgorithm
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

# ==============================
# 🔐 Konfiguration
# ==============================
KEYCLOAK_INTERNAL = "http://keycloak:8080"
OIDC_ISSUER = "https://login.workmate.test/realms/kit"
CLIENT_ID = "workmate-ui"
JWKS_URI = f"{KEYCLOAK_INTERNAL}/realms/kit/protocol/openid-connect/certs"

# Security dependency
auth_scheme = HTTPBearer()

# ==============================
# 🔑 JWKS laden & Cache halten
# ==============================
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

# ==============================
# 👤 Aktuellen Benutzer ermitteln
# ==============================
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
):
    token = creds.credentials
    try:
        # Header lesen & passenden Public Key finden
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
            options={"verify_aud": False},  # kein Audience-Check
            issuer=OIDC_ISSUER,
        )

        email = decoded.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Missing email claim")

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")

    # Mitarbeiter anhand E-Mail finden
    user = db.query(models.Employee).filter(models.Employee.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"No employee found for {email}")

    return user
