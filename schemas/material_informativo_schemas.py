from pydantic import BaseModel
from datetime import datetime

class MaterialInformativoBase(BaseModel):
    id_material_informativo: int
    contenido: str
    create_at: datetime
    create_by: str
    id_usuario: int

    class Config:
        orm_mode = True

class MaterialInformativoRequest(MaterialInformativoBase):
      class Config:
        orm_mode= True

        
class MaterialInformativoResponse(MaterialInformativoBase):
    id_material_informativo: int
    
    class Config:
        orm_mode=True