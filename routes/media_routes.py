from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import os

from db.database import get_db
from models.media_model import Media
from schemas.media_schemas import MediaRequest, MediaResponse
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

# Ruta para obtener todas las medias
@router.get('/media', status_code=status.HTTP_200_OK, response_model=List[MediaResponse])
def get_all_media(db: Session = Depends(get_db)):
    all_media = db.query(Media).all()
    return all_media

# Ruta para crear una nueva media
@router.post('/media', status_code=status.HTTP_201_CREATED, response_model=MediaResponse)
async def create_media(
    id_material_informativo: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    new_media = Media(
        image_path=file_path,
        id_material_informativo=id_material_informativo
    )
    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    return new_media

# Ruta para obtener una media por ID
@router.get("/media/{id_media}", response_model=MediaResponse)
def get_media(id_media: int, db: Session = Depends(get_db)):
    media = db.query(Media).filter(Media.id_media == id_media).first()
    if media is None:
        raise HTTPException(status_code=404, detail="Media no encontrada")
    return media

# Ruta para eliminar una media
@router.delete("/media/{id_media}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(
    id_media: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)

    media = db.query(Media).filter(Media.id_media == id_media).first()
    if media is None:
        raise HTTPException(status_code=404, detail="Media no encontrada")
    db.delete(media)
    db.commit()
    return {"message": "Media eliminada exitosamente"}

# Ruta para actualizar una media
@router.put("/media/{id_media}", response_model=MediaResponse)
def update_media(
    id_media: int,
    media_data: MediaRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)

    media = db.query(Media).filter(Media.id_media == id_media).first()
    if media is None:
        raise HTTPException(status_code=404, detail="Media no encontrada")
    
    media.id_material_informativo = media_data.id_material_informativo

    db.commit()
    db.refresh(media)
    return media
