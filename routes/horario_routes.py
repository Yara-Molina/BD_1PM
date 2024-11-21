from fastapi import APIRouter, HTTPException, Depends
from pymongo.collection import Collection
from typing import List
from db.database import get_mongo_db
from schemas.horario_schemas import HorarioSchema
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from middlewares.token import decode_access_token

router = APIRouter()
security = HTTPBearer()

def get_horario_collection(db=Depends(get_mongo_db)) -> Collection:
    return db["Horario"]

def authorize_request(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    user_info = decode_access_token(token)

    if not user_info or user_info.get("id_rol") != 1: 
        raise HTTPException(status_code=403, detail="Acceso denegado: Permisos insuficientes")

@router.get("/horarios", response_model=List[HorarioSchema])
async def get_horarios(horario_collection: Collection = Depends(get_horario_collection)):
    horarios = list(horario_collection.find())
    for horario in horarios:
        horario["id"] = str(horario["id"])  
    return horarios

@router.get("/horarios/{horario_id}", response_model=HorarioSchema)
async def get_horario_by_id(horario_id: str, horario_collection: Collection = Depends(get_horario_collection)):
    horario = horario_collection.find_one({"id": horario_id})
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    return horario

@router.post("/horarios", response_model=HorarioSchema)
async def create_horario(
    horario: HorarioSchema,
    horario_collection: Collection = Depends(get_horario_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    horario_dict = horario.dict(by_alias=True)

    if "id" not in horario_dict:
        horario_dict["id"] = str(horario_collection.estimated_document_count() + 1)
    horario_collection.insert_one(horario_dict)
    return horario_dict

@router.put("/horarios/{horario_id}", response_model=HorarioSchema)
async def update_horario(
    horario_id: str,
    horario: HorarioSchema,
    horario_collection: Collection = Depends(get_horario_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    horario_dict = horario.dict(by_alias=True)

    result = horario_collection.update_one({"id": horario_id}, {"$set": horario_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    return horario_dict

@router.delete("/horarios/{horario_id}", response_model=dict)
async def delete_horario(
    horario_id: str,
    horario_collection: Collection = Depends(get_horario_collection),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    authorize_request(credentials)
    result = horario_collection.delete_one({"id": horario_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    return {"message": "Horario eliminado correctamente"}
