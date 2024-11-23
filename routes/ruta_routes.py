from fastapi import APIRouter, HTTPException, Depends, status
from pymongo.collection import Collection
from typing import List
from db.database import get_mongo_db
from schemas.ruta_schemas import RutaSchema
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from middlewares.token import decode_access_token

router = APIRouter()
security = HTTPBearer()

def get_ruta_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["Rutas"]

def get_camion_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["Camiones"]

def get_puntos_recoleccion_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["PuntosRecoleccion"]

def authorize_request(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

def verify_camion_exists(id_camion: str, camion_collection: Collection):
    camion = camion_collection.find_one({"id": id_camion})
    if not camion:
        raise HTTPException(status_code=400, detail=f"El camión con ID {id_camion} no existe.")

def verify_punto_recoleccion_exists(id_punto: str, puntos_collection: Collection):
    punto = puntos_collection.find_one({"id": id_punto})
    if not punto:
        raise HTTPException(status_code=400, detail=f"El punto de recolección con ID {id_punto} no existe.")

@router.get("/rutas", response_model=List[RutaSchema])
async def get_rutas(ruta_collection: Collection = Depends(get_ruta_collection)):
    rutas = list(ruta_collection.find())
    return rutas

@router.get("/rutas/{ruta_id}", response_model=RutaSchema)
async def get_ruta_by_id(ruta_id: str, ruta_collection: Collection = Depends(get_ruta_collection)):
    ruta = ruta_collection.find_one({"id": ruta_id})
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta

@router.post("/rutas", response_model=RutaSchema)
async def create_ruta(
    ruta: RutaSchema,
    ruta_collection: Collection = Depends(get_ruta_collection),
    camion_collection: Collection = Depends(get_camion_collection),
    puntos_collection: Collection = Depends(get_puntos_recoleccion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)

    ruta_dict = ruta.dict(by_alias=True)

    if not ruta_dict.get("id_camion"):
        raise HTTPException(status_code=400, detail="El campo 'id_camion' es obligatorio.")
    if not ruta_dict.get("id_punto_recoleccion"):
        raise HTTPException(status_code=400, detail="El campo 'id_punto_recoleccion' es obligatorio.")

    verify_camion_exists(ruta_dict["id_camion"], camion_collection)
    verify_punto_recoleccion_exists(ruta_dict["id_punto_recoleccion"], puntos_collection)

    try:
        result = ruta_collection.insert_one(ruta_dict)
        ruta_dict["_id"] = str(result.inserted_id) 
        return RutaSchema(**ruta_dict).dict(by_alias=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la ruta: {str(e)}")

@router.put("/rutas/{ruta_id}", response_model=RutaSchema)
async def update_ruta(
    ruta_id: str,
    ruta: RutaSchema,
    ruta_collection: Collection = Depends(get_ruta_collection),
    camion_collection: Collection = Depends(get_camion_collection),
    puntos_collection: Collection = Depends(get_puntos_recoleccion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    ruta_dict = ruta.dict()

    verify_camion_exists(ruta_dict["id_camion"], camion_collection)
    verify_punto_recoleccion_exists(ruta_dict["id_punto_recoleccion"], puntos_collection)

    result = ruta_collection.update_one({"id": ruta_id}, {"$set": ruta_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta_dict

@router.delete("/rutas/{ruta_id}", response_model=dict)
async def delete_ruta(
    ruta_id: str,
    ruta_collection: Collection = Depends(get_ruta_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    result = ruta_collection.delete_one({"id": ruta_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return {"message": "Ruta eliminada correctamente"}
