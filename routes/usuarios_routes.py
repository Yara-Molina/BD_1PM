from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from models.usuarios_model import Usuario 
from schemas.usuarios_schemas import UsuarioRequest, UsuarioResponse
from middlewares.token import TokenMiddleware  

router = APIRouter()

def authorize_user(request: Request):
    user_info = getattr(request.state, "user", None)
    if not user_info:
        raise HTTPException(status_code=401, detail="User not authenticated")
    

    if user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions")

@router.get('/usuarios', status_code=status.HTTP_200_OK, response_model=List[UsuarioResponse])
def get_all_users(
    request: Request, 
    db: Session = Depends(get_db)
):
    authorize_user(request)
    all_users = db.query(Usuario).all()
    return all_users

@router.post('/usuarios', status_code=status.HTTP_201_CREATED, response_model=UsuarioResponse)
def create_user(
    user_request: UsuarioRequest,
    db: Session = Depends(get_db)
):
    new_user = Usuario(**user_request.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/usuarios/{id_usuario}", response_model=UsuarioResponse)
def get_user(
    request: Request,
    id_usuario: int,
    db: Session = Depends(get_db)
):
    authorize_user(request)
    user = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.delete("/usuarios/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    request: Request,
    id_usuario: int,
    db: Session = Depends(get_db)
):
    authorize_user(request)
    user = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}

@router.put("/usuarios/{id_usuario}", response_model=UsuarioResponse)
def update_user(
    request: Request,
    id_usuario: int,
    user_data: UsuarioRequest,
    db: Session = Depends(get_db)
):
    authorize_user(request)
    user = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.correo = user_data.correo
    user.id_rol = user_data.id_rol

    db.commit()
    db.refresh(user)
    return user