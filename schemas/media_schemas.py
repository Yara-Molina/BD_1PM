from pydantic import BaseModel
from datetime import datetime

class MediaBase(BaseModel):
    id_media: int  
    image_path: str
    id_material_informativo: int
    
    class Config:
        orm_mode= True     
    
class MediaRequest(MediaBase):
    class Config:
        orm_mode=True
        
class MediaResponse(MediaBase):
    id_media: int
    
    class Config:
        orm_mode=True
        
        