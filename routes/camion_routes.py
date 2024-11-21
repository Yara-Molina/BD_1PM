from fastapi import APIRouter, HTTPException, Depends, status
from pymongo.collection import Collection
from typing import List
from db.database import get_mongo_db
from schemas.camion_schemas import CamionSchema
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from middlewares.token import decode_access_token

router = APIRouter()
security = HTTPBearer()


def get_camion_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["Camiones"]


def authorize_request(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1: 
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")


@router.get("/camiones", response_model=List[CamionSchema])
async def get_camiones(camion_collection: Collection = Depends(get_camion_collection)):
    camiones = list(camion_collection.find())
    for camion in camiones:
        camion["id"] = str(camion["_id"])  
        del camion["_id"]
    return camiones

@router.get("/camiones/{camion_id}", response_model=CamionSchema)
async def get_camion_by_id(camion_id: str, camion_collection: Collection = Depends(get_camion_collection)):
    camion = camion_collection.find_one({"id": camion_id})
    if not camion:
        raise HTTPException(status_code=404, detail="Camión no encontrado")
    camion["id"] = str(camion["_id"])
    del camion["_id"] 
    return camion


@router.post("/camiones", response_model=CamionSchema)
async def create_camion(
    camion: CamionSchema,
    camion_collection: Collection = Depends(get_camion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    camion_dict = camion.dict(by_alias=True)
    if "id" not in camion_dict:
        camion_dict["id"] = str(camion_collection.estimated_document_count() + 1)

    result = camion_collection.insert_one(camion_dict)
    camion_dict["id"] = str(result.inserted_id)
    return camion_dict

@router.put("/camiones/{camion_id}", response_model=CamionSchema)
async def update_camion(
    camion_id: str,
    camion: CamionSchema,
    camion_collection: Collection = Depends(get_camion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    camion_dict = camion.dict(by_alias=True)

    result = camion_collection.update_one({"id": camion_id}, {"$set": camion_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Camión no encontrado")
    return camion_dict


@router.delete("/camiones/{camion_id}", response_model=dict)
async def delete_camion(
    camion_id: str,
    camion_collection: Collection = Depends(get_camion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    result = camion_collection.delete_one({"id": camion_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Camión no encontrado")
    return {"message": "Camión eliminado correctamente"}
