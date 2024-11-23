from pydantic import BaseModel, Field
from typing import Optional

class RutaSchema(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    Nombre_de_ruta: str
    id_camion: str
    id_punto_recoleccion: str

    class Config:
        allow_population_by_field_name = True
        alias_generator = str.lower
