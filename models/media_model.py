import sys
sys.path.append("C:\\Users\\cachi\\OneDrive\\Escritorio\\vsc\\FastApi\\APIREST (2)\\APIREST\\db")

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, DateTime
from db.database import Base
from sqlalchemy.orm import relationship

class Media(Base):
    __tablename__ = "Media"
    
    id_media = Column(Integer, primary_key=True, index=True)
    image_path = Column(String(100), nullable=False)
    id_material_informativo = Column(Integer, ForeignKey("Material_informativo.id_material_informativo"), nullable=False)
    
   
    material_informativo = relationship("MaterialInformativo", backref="material_media", foreign_keys=[id_material_informativo], remote_side=[id_material_informativo])
