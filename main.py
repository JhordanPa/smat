from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, get_db

# =====================================================
# CRITICAL: CREACIÓN DE LA BASE DE DATOS Y TABLAS
# Esta línea busca el archivo 'smat.db' y crea las tablas
# =====================================================
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SMAT Persistente")

# Esquemas de validación (Pydantic)
class EstacionCreate(BaseModel):
    id: int
    nombre: str
    ubicacion: str

class LecturaCreate(BaseModel):
    estacion_id: int
    valor: float

# ENDPOINTS REFACTORIZADOS
@app.post("/estaciones/", status_code=201)
def crear_estacion(estacion: EstacionCreate, db: Session = Depends(get_db)):
    # Convertimos el esquema de Pydantic a Modelo de SQLAlchemy
    nueva_estacion = models.EstacionDB(id=estacion.id, nombre=estacion.nombre, ubicacion=estacion.ubicacion)
    
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    
    return {"msj": "Estación guardada en DB", "data": nueva_estacion}

@app.post("/lecturas/", status_code=201)
def registrar_lectura(lectura: LecturaCreate, db: Session = Depends(get_db)):
    # Validar si la estación existe en la DB
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no existe")
        
    nueva_lectura = models.LecturaDB(valor=lectura.valor, estacion_id=lectura.estacion_id)
    
    db.add(nueva_lectura)
    db.commit()
    
    return {"status": "Lectura guardada en DB"}

@app.get("/estaciones/")
def listar_estaciones(db: Session = Depends(get_db)):
    # Le pedimos al archivero que nos traiga todas las estaciones guardadas
    estaciones_guardadas = db.query(models.EstacionDB).all()
    return estaciones_guardadas

@app.get("/estaciones/{id}/historial")
def obtener_historial_estacion(id: int, db: Session = Depends(get_db)):
    # El recepcionista va al archivero y busca solo las lecturas que coincidan con el ID
    historial = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).all()
    
    # Si la lista está vacía, avisamos que no hay datos
    if not historial:
        raise HTTPException(status_code=404, detail="No se encontraron lecturas para esta estación")
        
    return historial