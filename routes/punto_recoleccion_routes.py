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

def get_rutas_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["Rutas"]

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
    rutas_collection: Collection = Depends(get_rutas_collection),
    dias_recoleccion_collection: Collection = Depends(get_dias_recoleccion_collection),  # Nueva dependencia para verificar el día de recolección
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    ruta_existente = rutas_collection.find_one({"id": punto.id_Ruta})
    if not ruta_existente:
        raise HTTPException(status_code=404, detail="La ruta especificada no existe.")
    
    dia_recoleccion_existente = dias_recoleccion_collection.find_one({"id": punto.id_DiaRecoleccion})
    if not dia_recoleccion_existente:
        raise HTTPException(status_code=404, detail="El día de recolección especificado no existe.")
    
    punto_dict = punto.dict(by_alias=True)
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
