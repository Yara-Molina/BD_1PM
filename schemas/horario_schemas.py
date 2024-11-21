from pydantic import BaseModel, Field
from typing import Optional

class HorarioSchema(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    hora_inicio: str
    hora_fin: str

