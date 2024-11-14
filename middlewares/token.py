from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = "JHvgHFCTYVCYygtcvyt"
ALGORITHM = "HS256"

class TokenMiddleware(BaseHTTPMiddleware):
    def _init_(self, app):
        super().__init__(app)
        self.bearer = HTTPBearer()

    async def dispatch(self, request: Request, call_next):

        if request.method == "POST" and request.url.path == "/usuarios":
            print(f"Bypassing authentication for POST /usuarios")
            return await call_next(request)

        if request.url.path.startswith("/usuarios"):
            print(f"Validating token for method: {request.method} and path: {request.url.path}")
            
            credentials: HTTPAuthorizationCredentials = await self.bearer(request)
            if credentials:
                token = credentials.credentials
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    user_info = payload.get("user")
                    if not user_info:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User information not found in token",
                            headers={"WWW-Authenticate": "Bearer"},
                        )
                    request.state.user = user_info
                except ExpiredSignatureError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has expired",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                except InvalidTokenError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Credentials not provided",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return await call_next(request)