from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from auth import verify_password, create_access_token
from db.database import get_db
from models.usuarios_model import Usuario
from datetime import timedelta
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

router = APIRouter()

security = HTTPBearer()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(Usuario).filter(Usuario.correo == request.email).first()

        if not user or not verify_password(request.password, user.contrasena):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        token_data = {
            "sub": str(user.id_usuario),
            "id_rol": user.id_rol,
            "name": user.first_name
        }
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expiration_timestamp = int(expiration_time.timestamp() * 1000)

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        print(f"Token generado: {access_token}")
        return {"access_token": access_token, "token_type": "bearer", "rol": user.id_rol, "name": user.first_name, "id": user.id_usuario,"expires_at": expiration_timestamp  }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el proceso de login: {str(e)}"
        )


@router.get("/ruta-protegida", dependencies=[Depends(security)])
def ruta_protegida(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  
    return {"mensaje": "Acceso permitido", "token": token}