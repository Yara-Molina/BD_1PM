from pydantic import BaseModel, Field
from typing import Optional, List

class RutaSchema(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    Nombre_de_ruta: str
    id_puntos_recoleccion: List[str]

    class Config:
        allow_population_by_field_name = True
        alias_generator = str.lower