import sys
sys.path.append("C:\\Documentos\\Cuatrimestre 4\\APIREST\\db")

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, DateTime
from db.database import Base
from sqlalchemy.orm import relationship

class MaterialInformativo(Base):
    __tablename__ = "Material_informativo"
    
    id_material_informativo = Column(Integer, primary_key=True, index=True)
    contenido = Column(String(45), nullable=False)
    create_at = Column(TIMESTAMP, nullable=False)
    create_by = Column(String(45), nullable=False)
    id_usuario = Column(Integer, ForeignKey("Usuario.id_usuario"), nullable=False)
    id_media = Column(Integer, ForeignKey("Media.id_media"), nullable=False)

    
    usuario = relationship("Usuario", back_populates="material_informativo")
    media = relationship("Media", backref="material_media", foreign_keys=[id_media])
