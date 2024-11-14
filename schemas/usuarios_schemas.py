from pydantic import BaseModel
from datetime import datetime


class UsuarioBase(BaseModel):
    id_usuario: int
    first_name: str
    last_name: str
    correo: str
    contrasena: str
    create_at: datetime
    create_by: str
    id_rol: int 

class UsuarioRequest(UsuarioBase):
     class config:
      orm_mode=True

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    

    class Config:
        orm_mode = True