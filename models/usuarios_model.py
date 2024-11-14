from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Usuario(Base):
    __tablename__ = "Usuario"
  
    id_usuario = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)  
    last_name = Column(String(100), nullable=False)      
    contrasena = Column(String(100), nullable=False) 
    correo = Column(String(100), nullable=False)      
    create_at = Column(TIMESTAMP, nullable=False)
    create_by = Column(String(45), nullable=False)
    
    
    id_rol = Column(Integer, ForeignKey("Roles.id_rol"), nullable=False)
    
  
    role = relationship("Roles", back_populates="usuarios") 
    notificaciones = relationship("Notification", back_populates="usuario")
    material_informativo = relationship("MaterialInformativo", back_populates="usuario")
