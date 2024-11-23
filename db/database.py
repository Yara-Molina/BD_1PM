from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import Generator

SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://max:@localhost/postgres'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


MONGO_URI = "mongodb+srv://233295:vqQJoCCYobQgQDWi@max.rwdsl.mongodb.net/?retryWrites=true&w=majority&appName=Max"
mongo_client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
mongo_db = mongo_client["Rutas_TuxBin"]

def get_mongo_db() -> Generator:
    try:
        yield mongo_db
    except Exception as e:
        print(f"Error conectando a MongoDB: {e}")
        raise e

camiones_collection = mongo_db["Camiones"]
dia_recoleccion_collection = mongo_db["Dia_Recoleccion"]
horario_collection = mongo_db["Horario"]
puntos_recoleccion_collection = mongo_db["Puntos_Recoleccion"]
rutas_collection = mongo_db["Rutas"]
