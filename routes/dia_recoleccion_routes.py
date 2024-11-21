from fastapi import APIRouter, HTTPException, Depends
from pymongo.collection import Collection
from typing import List
from db.database import get_mongo_db
from schemas.dia_recoleccion_schemas import DiaRecoleccionSchema
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from middlewares.token import decode_access_token

router = APIRouter()
security = HTTPBearer()

def get_dia_recoleccion_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["DiaRecoleccion"]

def get_horario_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["Horario"]

def authorize_request(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1: 
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

@router.get("/dias_recoleccion", response_model=List[DiaRecoleccionSchema])
async def get_dias_recoleccion(dia_recoleccion_collection: Collection = Depends(get_dia_recoleccion_collection)):
    dias = list(dia_recoleccion_collection.find())
    for dia in dias:
        dia["_id"] = str(dia["_id"])  
    return dias

@router.get("/dias_recoleccion/{dia_id}", response_model=DiaRecoleccionSchema)
async def get_dia_recoleccion_by_id(dia_id: str, dia_recoleccion_collection: Collection = Depends(get_dia_recoleccion_collection)):
    dia = dia_recoleccion_collection.find_one({"id": dia_id})
    if not dia:
        raise HTTPException(status_code=404, detail="Día de recolección no encontrado")
    return dia

def verify_horario_exists(horario_id: str, horario_collection: Collection):
    horario = horario_collection.find_one({"id": horario_id})
    if not horario:
        raise HTTPException(status_code=400, detail=f"El horario con ID {horario_id} no existe.")

@router.post("/dias_recoleccion", response_model=DiaRecoleccionSchema)
async def create_dia_recoleccion(
    dia: DiaRecoleccionSchema,
    dia_recoleccion_collection: Collection = Depends(get_dia_recoleccion_collection),
    horario_collection: Collection = Depends(get_horario_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    dia_dict = dia.dict(by_alias=True)

    verify_horario_exists(dia_dict["id_Horario"], horario_collection)

    if "id" not in dia_dict:
        dia_dict["id"] = str(dia_recoleccion_collection.estimated_document_count() + 1)

    dia_recoleccion_collection.insert_one(dia_dict)
    return dia_dict

@router.put("/dias_recoleccion/{dia_id}", response_model=DiaRecoleccionSchema)
async def update_dia_recoleccion(
    dia_id: str,
    dia: DiaRecoleccionSchema,
    dia_recoleccion_collection: Collection = Depends(get_dia_recoleccion_collection),
    horario_collection: Collection = Depends(get_horario_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    dia_dict = dia.dict(by_alias=True)

    verify_horario_exists(dia_dict["id_Horario"], horario_collection)

    result = dia_recoleccion_collection.update_one({"id": dia_id}, {"$set": dia_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Día de recolección no encontrado")
    return dia_dict

@router.delete("/dias_recoleccion/{dia_id}", response_model=dict)
async def delete_dia_recoleccion(
    dia_id: str,
    dia_recoleccion_collection: Collection = Depends(get_dia_recoleccion_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    result = dia_recoleccion_collection.delete_one({"id": dia_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Día de recolección no encontrado")
    return {"message": "Día de recolección eliminado correctamente"}
