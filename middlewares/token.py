from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from typing import Optional, Dict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response

SECRET_KEY = "JHvgHFCTYVCYygtcvyt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        raise ValueError(f"Error verificando la contraseña: {str(e)}")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict]:
    try:
        # Decodificar el payload del token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Token decodificado: {payload}")  # Muestra el contenido decodificado

        # Verificar que contiene el campo 'sub'
        if "sub" not in payload:
            raise ValueError("Token no contiene el campo 'sub'")
        return payload
    except jwt.PyJWTError as e:
        print(f"Error al decodificar el token: {e}") 
        raise ValueError(f"Error al decodificar el token: {str(e)}")
    except ValueError as e:
        print(f"Error en la validación del token: {e}")  
        raise ValueError(f"Token mal formado: {str(e)}")



def extract_user_info_from_token(token: str) -> Optional[str]:
    decoded_token = decode_access_token(token)
    return decoded_token.get("sub") if decoded_token else None

class TokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        open_paths = ["/", "/usuarios", "/favicon.ico", "/login"]

        if any(request.url.path.startswith(open_path) for open_path in open_paths):
            return await call_next(request)

        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
            try:
                user_info = decode_access_token(token)
                print(f"Información decodificada: {user_info}")  # Muestra la información del usuario
                if user_info:
                    request.state.user = user_info
                    print(f"User info guardado en request.state.user: {request.state.user}")  # Verifica que se guardó correctamente
            except Exception as e:
                return Response(content=f"Token inválido: {str(e)}", status_code=401)
        else:
            return Response(content="Token faltante o mal formado", status_code=401)

        return await call_next(request)
