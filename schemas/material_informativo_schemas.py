from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MaterialInformativoBase(BaseModel):
    titulo: str
    contenido: str
    id_usuario: int
    path_imagen: Optional[str]=None
    

    class Config:
        orm_mode = True

class MaterialInformativoRequest(MaterialInformativoBase):
      pass

class MaterialInformativoResponse(MaterialInformativoBase):
    id_material_informativo: int

    class Config:
        orm_mode = True