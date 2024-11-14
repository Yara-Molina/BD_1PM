from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from db.database import get_db
from models.roles_model import Roles  
from schemas.roles_schemas import RolRequest, RolResponse  

router = APIRouter()

@router.get('/roles', status_code=status.HTTP_200_OK, response_model=List[RolResponse])
def get_all_roles(db: Session = Depends(get_db)):
    all_roles = db.query(Roles).all()
    return all_roles


@router.post('/roles', status_code=status.HTTP_201_CREATED, response_model=RolResponse)
def create_role(post_role: RolRequest, db: Session = Depends(get_db)):
    new_role = Roles(**post_role.dict())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@router.get("/roles/{id_rol}", response_model=RolResponse)
def get_role(id_rol: int, db: Session = Depends(get_db)):
    role = db.query(Roles).filter(Roles.id_rol == id_rol).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return role


@router.delete("/roles/{id_rol}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(id_rol: int, db: Session = Depends(get_db)):
    role = db.query(Roles).filter(Roles.id_rol == id_rol).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    db.delete(role)
    db.commit()
    return {"message": "Rol eliminado exitosamente"}

@router.put("/roles/{id_rol}", response_model=RolResponse)
def update_role(
    id_rol: int,
    role_data: RolRequest,
    db: Session = Depends(get_db)
):
    role = db.query(Roles).filter(Roles.id_rol == id_rol).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    role.name = role_data.name
    role.create_at = role_data.create_at
    role.create_by = role_data.create_by

    db.commit()
    db.refresh(role)
    return role
