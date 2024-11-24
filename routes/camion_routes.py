from fastapi import APIRouter, HTTPException, Depends, status
from pymongo.collection import Collection
from typing import List
from db.database import get_mongo_db
from schemas.camion_schemas import CamionSchema
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from middlewares.token import decode_access_token
from bson import ObjectId

router = APIRouter()
security = HTTPBearer()

def get_camion_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["Camiones"]

def authorize_request(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    user_info = decode_access_token(token)
    if not user_info or user_info.get("id_rol") != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

def format_camion(camion):
    if camion:
        camion["id"] = str(camion["_id"])
        del camion["_id"]
    return camion

@router.get("/camiones", response_model=List[CamionSchema])
async def get_camiones(camion_collection: Collection = Depends(get_camion_collection)):
    try:
        camiones = list(camion_collection.find())
        return [format_camion(camion) for camion in camiones]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los camiones: {str(e)}"
        )

@router.get("/camiones/{camion_id}", response_model=CamionSchema)
async def get_camion_by_id(
    camion_id: str, 
    camion_collection: Collection = Depends(get_camion_collection)
):
    try:
        camion = camion_collection.find_one({"id": camion_id})
        
        if not camion:
            try:
                obj_id = ObjectId(camion_id)
                camion = camion_collection.find_one({"_id": obj_id})
            except:
                raise HTTPException(
                    status_code=404,
                    detail="ID de camión inválido"
                )
        
        if not camion:
            raise HTTPException(
                status_code=404,
                detail="Camión no encontrado"
            )
            
        return format_camion(camion)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el camión: {str(e)}"
        )

@router.post("/camiones", response_model=CamionSchema)
async def create_camion(
    camion: CamionSchema,
    camion_collection: Collection = Depends(get_camion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        authorize_request(credentials)
        
        camion_dict = camion.dict(by_alias=True, exclude_unset=True)
        
        result = camion_collection.insert_one(camion_dict)
        
        nuevo_camion = camion_collection.find_one({"_id": result.inserted_id})
        
        return format_camion(nuevo_camion)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el camión: {str(e)}"
        )

@router.put("/camiones/{camion_id}", response_model=CamionSchema)
async def update_camion(
    camion_id: str,
    camion: CamionSchema,
    camion_collection: Collection = Depends(get_camion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        authorize_request(credentials)
        
        camion_dict = camion.dict(by_alias=True, exclude_unset=True)
        
        result = camion_collection.update_one(
            {"id": camion_id},
            {"$set": camion_dict}
        )
        
        if result.matched_count == 0:
            try:
                obj_id = ObjectId(camion_id)
                result = camion_collection.update_one(
                    {"_id": obj_id},
                    {"$set": camion_dict}
                )
            except:
                raise HTTPException(
                    status_code=404,
                    detail="ID de camión inválido"
                )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Camión no encontrado"
            )
            
        camion_actualizado = camion_collection.find_one({
            "$or": [
                {"id": camion_id},
                {"_id": ObjectId(camion_id)}
            ]
        })
        
        return format_camion(camion_actualizado)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar el camión: {str(e)}"
        )

@router.delete("/camiones/{camion_id}", response_model=dict)
async def delete_camion(
    camion_id: str,
    camion_collection: Collection = Depends(get_camion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        authorize_request(credentials)
        
        result = camion_collection.delete_one({
            "$or": [
                {"id": camion_id},
                {"_id": ObjectId(camion_id)}
            ]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Camión no encontrado"
            )
            
        return {"message": "Camión eliminado correctamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar el camión: {str(e)}"
        )