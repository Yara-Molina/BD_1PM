from pydantic import BaseModel, Field
from typing import Optional

class CamionSchema(BaseModel):
    id: Optional[str] = Field(None, alias="id")  
    Matricula: str
    Numero_Unidad: int

    class Config:
        allow_population_by_field_name = True
        alias_generator = str.lower 
