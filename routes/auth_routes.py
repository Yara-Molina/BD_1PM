from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from auth import verify_password, create_access_token
from db.database import get_db
from models.usuarios_model import Usuario
from datetime import timedelta

router = APIRouter()

security = HTTPBearer()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    try:
        user = db.query(Usuario).filter(Usuario.correo == email).first()

        if not user or not verify_password(password, user.contrasena):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        token_data = {
            "sub": str(user.id_usuario),
            "id_rol": user.id_rol
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        print(f"Token generado: {access_token}")

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el proceso de login: {str(e)}"
        )

@router.get("/ruta-protegida", dependencies=[Depends(security)])
def ruta_protegida(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  
    return {"mensaje": "Acceso permitido", "token": token}
