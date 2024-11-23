from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.collection import Collection
from typing import List
from db.database import get_mongo_db
from schemas.punto_recoleccion_schemas import PuntoRecoleccionSchema
from middlewares.token import decode_access_token

router = APIRouter()
security = HTTPBearer()

def authorize_request(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

def get_puntos_recoleccion_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["PuntosRecoleccion"]

def get_dias_recoleccion_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["DiaRecoleccion"]

@router.get("/puntos_recoleccion", response_model=List[PuntoRecoleccionSchema])
async def get_puntos_recoleccion(puntos_collection: Collection = Depends(get_puntos_recoleccion_collection)):
    puntos = list(puntos_collection.find())
    for punto in puntos:
        punto["_id"] = str(punto["_id"]) 
    return puntos

@router.get("/puntos_recoleccion/{punto_id}", response_model=PuntoRecoleccionSchema)
async def get_punto_recoleccion_by_id(
    punto_id: str, 
    puntos_collection: Collection = Depends(get_puntos_recoleccion_collection)
):
    punto = puntos_collection.find_one({"id": punto_id})
    if not punto:
        raise HTTPException(status_code=404, detail="Punto de recolección no encontrado")
    punto["id"] = str(punto["_id"])
    del punto["_id"]
    return punto

@router.post("/puntos_recoleccion", response_model=PuntoRecoleccionSchema)
async def create_punto_recoleccion(
    punto: PuntoRecoleccionSchema,
    puntos_collection: Collection = Depends(get_puntos_recoleccion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)

    punto_dict = punto.dict(by_alias=True)

    if "geojson" not in punto_dict or not isinstance(punto_dict["geojson"], dict):
        raise HTTPException(status_code=400, detail="El campo 'geojson' es obligatorio y debe ser un objeto válido.")

    punto_dict["id"] = str(puntos_collection.estimated_document_count() + 1)
    puntos_collection.insert_one(punto_dict)
    return punto_dict

@router.put("/puntos_recoleccion/{id_punto}", response_model=PuntoRecoleccionSchema)
async def update_punto_recoleccion(
    id_punto: str,
    punto: PuntoRecoleccionSchema,
    puntos_collection: Collection = Depends(get_puntos_recoleccion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)

    punto_dict = punto.dict(by_alias=True)

    if "geojson" not in punto_dict or not isinstance(punto_dict["geojson"], dict):
        raise HTTPException(status_code=400, detail="El campo 'geojson' es obligatorio y debe ser un objeto válido.")

    result = puntos_collection.update_one({"id": id_punto}, {"$set": punto_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Punto de recolección no encontrado")
    return punto_dict

@router.delete("/puntos_recoleccion/{id_punto}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_punto_recoleccion(
    id_punto: str,
    puntos_collection: Collection = Depends(get_puntos_recoleccion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    result = puntos_collection.delete_one({"id": id_punto})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Punto de recolección no encontrado")
    return {"message": "Punto de recolección eliminado exitosamente"}
