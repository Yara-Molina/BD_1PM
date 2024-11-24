from pydantic import BaseModel
from datetime import datetime


class NotificationBase(BaseModel):
    titulo: str
    texto: str
    tiempo_activo: datetime
    create_at: datetime
    create_by: str
    id_usuario: int 
    
    class Config:
        orm_mode= True
        
class NotificationRequest(NotificationBase):
    class Config:
        orm_mode=True
        
class NotificationResponse(NotificationBase):
    id_notificaciones: int
    
    class Config:
        orm_mode=True