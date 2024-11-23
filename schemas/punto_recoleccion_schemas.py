from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class PuntoRecoleccionSchema(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    Calle: str
    Colonia: str
    CP: int
    geojson: Dict[str, Any]
    id_DiaRecoleccion: str

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        alias_generator = str.lower
