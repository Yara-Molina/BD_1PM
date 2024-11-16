from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from middlewares.token import verify_password, create_access_token, decode_access_token
from models.usuarios_model import Usuario  

def authenticate_user(correo: str, password: str, db: Session = Depends(get_db)):

    user = db.query(Usuario).filter(Usuario.correo == correo).first() 
    
    if user and verify_password(password, user.contrasena): 
        user_data = {"sub": user.correo, "id_rol": user.id_rol} 
        access_token = create_access_token(user_data)  
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

def decode_token_and_get_user_info(token: str):
    try:
        return decode_access_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
