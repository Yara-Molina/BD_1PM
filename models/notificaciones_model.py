import sys
sys.path.append("C:\\Users\\cachi\\OneDrive\\Escritorio\\vsc\\FastApi\\APIREST (2)\\APIREST\\db")

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, DateTime
from db.database import Base
from sqlalchemy.orm import relationship

class Notification(Base):
    __tablename__ = "Notificacion"
  
    id_notificaciones = Column(Integer, primary_key=True, index=True,autoincrement=True )
    titulo = Column(String(100), nullable=False)  
    texto = Column(String(255), nullable=False)  
    tiempo_activo = Column(DateTime, nullable=False)
    create_at = Column(TIMESTAMP, nullable=False)
    create_by = Column(String(45), nullable=False)
    id_usuario = Column(Integer, ForeignKey("Usuario.id_usuario"), nullable=False)
    
    usuario = relationship("Usuario", back_populates="notificaciones")
