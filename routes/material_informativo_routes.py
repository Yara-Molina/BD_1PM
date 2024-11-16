from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from models.material_informativo_model import MaterialInformativo  
from schemas.material_informativo_schemas import MaterialInformativoRequest, MaterialInformativoResponse  
from middlewares.token import decode_access_token

router = APIRouter()
security = HTTPBearer()

def authorize_request(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

# Ruta para obtener todos los materiales informativos
@router.get('/material-informativo', status_code=status.HTTP_200_OK, response_model=List[MaterialInformativoResponse])
def get_all_material_informativo(db: Session = Depends(get_db)):
    all_material_informativo = db.query(MaterialInformativo).all()
    return all_material_informativo

# Ruta para crear un nuevo material informativo
@router.post('/material-informativo', status_code=status.HTTP_201_CREATED, response_model=MaterialInformativoResponse)
def create_material_informativo(
    post_material_informativo: MaterialInformativoRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    new_material_informativo = MaterialInformativo(**post_material_informativo.dict())
    db.add(new_material_informativo)
    db.commit()
    db.refresh(new_material_informativo)
    return new_material_informativo

# Ruta para obtener un material informativo por ID
@router.get("/material-informativo/{id_material_informativo}", response_model=MaterialInformativoResponse)
def get_material_informativo(id_material_informativo: int, db: Session = Depends(get_db)):
    material_informativo = db.query(MaterialInformativo).filter(MaterialInformativo.id_material_informativo == id_material_informativo).first()
    if material_informativo is None:
        raise HTTPException(status_code=404, detail="Material informativo no encontrado")
    return material_informativo

# Ruta para eliminar un material informativo
@router.delete("/material-informativo/{id_material_informativo}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material_informativo(
    id_material_informativo: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    material_informativo = db.query(MaterialInformativo).filter(MaterialInformativo.id_material_informativo == id_material_informativo).first()
    if material_informativo is None:
        raise HTTPException(status_code=404, detail="Material informativo no encontrado")
    db.delete(material_informativo)
    db.commit()
    return {"message": "Material informativo eliminado exitosamente"}

# Ruta para actualizar un material informativo
@router.put("/material-informativo/{id_material_informativo}", response_model=MaterialInformativoResponse)
def update_material_informativo(
    id_material_informativo: int,
    material_informativo_data: MaterialInformativoRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    material_informativo = db.query(MaterialInformativo).filter(MaterialInformativo.id_material_informativo == id_material_informativo).first()
    if material_informativo is None:
        raise HTTPException(status_code=404, detail="Material informativo no encontrado")
    
    # Actualizar los campos del material informativo con los datos nuevos
    material_informativo.contenido = material_informativo_data.contenido
    material_informativo.create_at = material_informativo_data.create_at
    material_informativo.create_by = material_informativo_data.create_by

    db.commit()
    db.refresh(material_informativo)
    return material_informativo
