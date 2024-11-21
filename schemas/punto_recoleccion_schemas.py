from pydantic import BaseModel, Field
from typing import Optional

class PuntoRecoleccionSchema(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    Calle: str
    Colonia: str
    CP: int
    Altitud: str
    Latitud: str
    id_Ruta: str = Field(..., alias="id_ruta")
    id_DiaRecoleccion: str 

    class Config:
        allow_population_by_field_name = True 
        orm_mode = True 
        alias_generator = str.lower