from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import HTTPException

from supabase_client import supabase

security = HTTPBearer(auto_error=False)


def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Access token required"

        )
    try:
        response = supabase.auth.get_user(credentials.credentials)
        if response.user is None:
            raise Exception("User not found")
        return response.user
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="invalid or expired token"
        )
