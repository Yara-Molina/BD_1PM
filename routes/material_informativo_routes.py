from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
import os

from db.database import get_db
from models.material_informativo_model import MaterialInformativo
from schemas.material_informativo_schemas import MaterialInformativoRequest, MaterialInformativoResponse
from middlewares.token import decode_access_token

router = APIRouter()

security = HTTPBearer()
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def authorize_request(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

BASE_URL = "http://127.0.0.1:8000"  # Asegúrate de usar la ruta correcta

@router.get('/material-informativo', status_code=status.HTTP_200_OK, response_model=List[MaterialInformativoResponse])
def get_all_material_informativo(db: Session = Depends(get_db)):
    materials = db.query(MaterialInformativo).all()

    for material in materials:
        material.path_imagen = f"{BASE_URL}{material.path_imagen}"  # Ahora se añade correctamente a la URL completa

    return materials


@router.get('/material-informativo/{id_material_informativo}', status_code=status.HTTP_200_OK, response_model=MaterialInformativoResponse)
def get_material_informativo_by_id(
    id_material_informativo: int,
    db: Session = Depends(get_db)
):
    material = db.query(MaterialInformativo).filter(MaterialInformativo.id_material_informativo == id_material_informativo).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material informativo no encontrado")
    return material

@router.post('/material-informativo', status_code=status.HTTP_201_CREATED, response_model=MaterialInformativoResponse)
async def create_material_informativo(
    titulo: str = Form(...),
    contenido: str = Form(...),
    id_usuario: int = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)

    file_path = None
    image_url = None
    if file:
        filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        image_url = f"/uploads/{filename}" 

    new_material_informativo = MaterialInformativo(
        titulo=titulo,
        contenido=contenido,
        id_usuario=id_usuario,
        path_imagen=image_url
    )
    db.add(new_material_informativo)
    db.commit()
    db.refresh(new_material_informativo)
    return new_material_informativo

@router.put('/material-informativo/{id_material_informativo}', response_model=MaterialInformativoResponse)
async def update_material_informativo(
    id_material_informativo: int,
    titulo: str = Form(...),
    contenido: str = Form(...),
    id_usuario: int = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)

    material_informativo = db.query(MaterialInformativo).filter(
        MaterialInformativo.id_material_informativo == id_material_informativo
    ).first()

    if not material_informativo:
        raise HTTPException(status_code=404, detail="Material informativo no encontrado")

    material_informativo.titulo = titulo
    material_informativo.contenido = contenido
    material_informativo.id_usuario = id_usuario

    if file:
        filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        material_informativo.path_imagen = f"/uploads/{filename}"

    db.commit()
    db.refresh(material_informativo)
    return material_informativo

@router.delete('/material-informativo/{id_material_informativo}', status_code=status.HTTP_204_NO_CONTENT)
def delete_material_informativo(
    id_material_informativo: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)

    material_informativo = db.query(MaterialInformativo).filter(
        MaterialInformativo.id_material_informativo == id_material_informativo
    ).first()

    if not material_informativo:
        raise HTTPException(status_code=404, detail="Material informativo no encontrado")

    db.delete(material_informativo)
    db.commit()
    return {"message": "Material informativo eliminado exitosamente"}