
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from db.database import get_db
from models.notificaciones_model import Notification
from schemas.notifiacion_schemas import NotificationRequest, NotificationResponse

router = APIRouter()

# Ruta para obtener todas las notificaciones
@router.get('/notificaciones', status_code=status.HTTP_200_OK, response_model=List[NotificationResponse])
def get_all_notifications(db: Session = Depends(get_db)):
    all_notifications = db.query(Notification).all()
    for notification in all_notifications:
        print(f'ID: {notification.id_notificaciones}, Titulo: {notification.titulo}, Texto: {notification.texto}')   
    return all_notifications

# Ruta para crear una nueva notificación
@router.post('/notificaciones', status_code=status.HTTP_201_CREATED, response_model=NotificationResponse)
def create_notification(post_notification: NotificationRequest, db: Session = Depends(get_db)):
    new_notification = Notification(**post_notification.dict())
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

# Ruta para obtener una notificación por ID
@router.get("/notificaciones/{id_notificaciones}", response_model=NotificationResponse)
def get_notification(id_notificaciones: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id_notificaciones == id_notificaciones).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return notification

@router.delete("/notificaciones/{id_notificaciones}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(id_notificaciones: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id_notificaciones == id_notificaciones).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db.delete(notification)
    db.commit()
    return {"message": "Notificación eliminada exitosamente"}

@router.put("/notificaciones/{id_notificaciones}", response_model=NotificationResponse)
def update_notification(
    id_notificaciones: int,
    notification_data: NotificationRequest,
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(Notification.id_notificaciones == id_notificaciones).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    # Actualizar los campos de la notificación con los datos nuevos
    notification.titulo = notification_data.titulo
    notification.texto = notification_data.texto
    notification.tiempo_activo = notification_data.tiempo_activo

    db.commit()
    db.refresh(notification)
    return notification

