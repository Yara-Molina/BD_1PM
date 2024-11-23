from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id_notificaciones: int  
    titulo: str
    texto: str
    tiempo_activo: datetime
    create_at: datetime
    create_by: str

          
class UsuarioResponse(BaseModel):
    usuario_id: int
    first_name: str
    last_name: str
    correo: str
    create_at: datetime
    create_by: str
       
    
class RolResponse(BaseModel):
    id_rol: int  
    name: str
    create_at: datetime
    create_by: str
    
    
class MaterialInformativoResponse(BaseModel):
    titulo: str
    contenido: str
    id_usuario: int

class Config:
        orm_mode = True    