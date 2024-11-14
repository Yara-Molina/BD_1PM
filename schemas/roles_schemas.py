from pydantic import BaseModel
from datetime import datetime

class RolBase(BaseModel):
    id_rol: int  
    name: str
    create_at: datetime
    create_by: str
    
    class Config:
        orm_mode= True
        
class RolRequest(RolBase):
    class Config:
        orm_mode=True
        
class RolResponse(RolBase):
    id_rol: int
    
    class Config:
        orm_mode=True