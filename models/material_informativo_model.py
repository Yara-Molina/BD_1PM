import sys
sys.path.append("C:\\Users\\cachi\\OneDrive\\Escritorio\\vsc\\FastApi\\APIREST (2)\\APIREST\\db")

from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base
from sqlalchemy.orm import relationship

class MaterialInformativo(Base):
    __tablename__ = "Material_informativo"

    id_material_informativo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(45), nullable=False)
    contenido = Column(String(255), nullable=False)
    id_usuario = Column(Integer, ForeignKey("Usuario.id_usuario"), nullable=False)
    path_imagen = Column(String(255), nullable=True)

    usuario = relationship("Usuario", back_populates="material_informativo")
