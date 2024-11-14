from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from db.database import Base

class Roles(Base):
    __tablename__ = "Roles"
  
    id_rol = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  
    create_at = Column(TIMESTAMP, nullable=False)
    create_by = Column(String(45), nullable=False)
    
    
    usuarios = relationship("Usuario", back_populates="role")  
