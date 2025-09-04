from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional

from .config import get_settings


auth_scheme = HTTPBearer(auto_error=False)


async def get_current_user_optional(
	credentials: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme),
):
	settings = get_settings()
	if settings.access_token is None:
		return None
	if not credentials or credentials.scheme.lower() != "bearer":
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
	if credentials.credentials != settings.access_token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	return {"sub": "gateway-user"}


async def require_user(user=Depends(get_current_user_optional)):
	if user is None:
		return None
	return user
