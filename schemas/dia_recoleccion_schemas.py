from pydantic import BaseModel, Field
from typing import Optional

class DiaRecoleccionSchema(BaseModel):
    id: Optional[str] = Field(None, alias="id") 
    dia: str 
    id_Horario: str 
    dia_de_recoleccion: bool  
