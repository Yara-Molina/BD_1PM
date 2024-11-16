from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from models.usuarios_model import Usuario
from schemas.usuarios_schemas import UsuarioRequest, UsuarioResponse
from middlewares.token import get_password_hash, decode_access_token

router = APIRouter()
security = HTTPBearer()


@router.get("/usuarios/correo/{correo}", response_model=UsuarioResponse)
def get_user_by_correo(
    correo: str,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

    user = db.query(Usuario).filter(Usuario.correo == correo).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get('/usuarios', status_code=status.HTTP_200_OK, response_model=List[UsuarioResponse])
def get_all_users(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

    all_users = db.query(Usuario).all()
    return all_users


@router.post('/usuarios', status_code=status.HTTP_201_CREATED, response_model=UsuarioResponse)
def create_user(
    user_request: UsuarioRequest,
    db: Session = Depends(get_db),
):
    hashed_password = get_password_hash(user_request.contrasena)
    user_data = user_request.dict(exclude={"contrasena"})
    new_user = Usuario(**user_data, contrasena=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/usuarios/{id_usuario}", response_model=UsuarioResponse)
def get_user(
    id_usuario: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

    user = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.delete("/usuarios/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id_usuario: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

    user = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}


@router.put("/usuarios/{id_usuario}", response_model=UsuarioResponse)
def update_user(
    id_usuario: int,
    user_data: UsuarioRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

    user = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user_data.contrasena:
        user_data.contrasena = get_password_hash(user_data.contrasena)

    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.correo = user_data.correo
    user.id_rol = user_data.id_rol
    user.contrasena = user_data.contrasena

    db.commit()
    db.refresh(user)
    return user
