import requests
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jwt.algorithms import RSAAlgorithm

# interne Keycloak-Adresse (innerhalb Docker)
KEYCLOAK_INTERNAL = "http://keycloak:8080"
# externer Issuer (laut Token-Claim)
OIDC_ISSUER = "https://login.workmate.test/realms/kit"

# JWKS-Endpunkt (Public Keys)
JWKS_URI = f"{KEYCLOAK_INTERNAL}/realms/kit/protocol/openid-connect/certs"

# Security scheme für FastAPI
auth_scheme = HTTPBearer()

# JWKS einmalig laden (optional mit Cache)
def get_jwks():
    try:
        resp = requests.get(JWKS_URI)
        resp.raise_for_status()
        jwks = resp.json()
        return {key["kid"]: key for key in jwks["keys"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der JWKS: {e}")

def verify_token(token: str):
    keys = get_jwks()
    header = jwt.get_unverified_header(token)
    key_data = keys.get(header.get("kid"))
    if not key_data:
        raise HTTPException(status_code=401, detail="Ungültiger Token-Header")

    public_key = RSAAlgorithm.from_jwk(key_data)

    try:
        decoded = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience="account",  # oder verify_aud=False falls nötig
            issuer=OIDC_ISSUER,
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token abgelaufen")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Ungültiges Token: {e}")

# -----------------------------------------------------
# 💡 Diese Funktion erwartet dein Backend (import!)
# -----------------------------------------------------
def get_current_user(credentials=Depends(auth_scheme)):
    token = credentials.credentials
    user = verify_token(token)
    return user
