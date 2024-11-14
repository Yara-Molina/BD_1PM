from fastapi import FastAPI, Depends, status, HTTPException
from middlewares.token import TokenMiddleware
from typing import List
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import sys
sys.path.append("C:\\Documentos\\Cuatrimestre 4\\APIREST\\db")

from db.database import engine, get_db, Base
from models import notificaciones_model 
from sqlalchemy.orm import Session
from routes.notificacion_routes import router as notificaciones_router
from routes.usuarios_routes import router as usuario_router
from routes.roles_routes import router as rol_router
from routes.media_routes import router as media_router
from routes.material_informativo_routes import router as material_info_router


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(TokenMiddleware)


@app.get('/')
def index():
    return {'message': 'Server alive!', 'time': datetime.now()}

app.include_router(notificaciones_router, tags=["Notificacion"])
app.include_router(usuario_router, tags=["Usuario"])
app.include_router(rol_router, tags=["Rol"])
app.include_router(media_router, tags=["Media"])
app.include_router(material_info_router, tags=["Material_info"])