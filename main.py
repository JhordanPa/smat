from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
app = FastAPI(title="SMAT API")
class Estacion(BaseModel):
    id: int
    nombre: str
    ubicacion: str
db_estaciones = []
@app.post("/estaciones/", status_code=201)
async def crear_estacion(estacion: Estacion):
    db_estaciones.append(estacion)
    return {"msj": "Estación creada", "data": estacion}
@app.get("/estaciones/", response_model=List[Estacion])
async def listar_estaciones():
    return db_estaciones

class Lectura(BaseModel):
    estacion_id: int
    valor: float
db_lecturas = []
@app.post("/lecturas/", status_code=201)
async def registrar_lectura(lectura: Lectura):
    db_lecturas.append(lectura)
    return {"status": "Lectura recibida"}

@app.get("/estaciones/{id}/riesgo")
async def obtener_riesgo(id: int):
# 1. Validar existencia de la estación (Requisito 404)
    estacion_existe = any(e.id == id for e in db_estaciones)
    if not estacion_existe:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
# 2. Filtrar lecturas de la estación
    lecturas = [l for l in db_lecturas if l.estacion_id == id]
    if not lecturas:
        return {"id": id, "nivel": "SIN DATOS", "valor": 0}
# 3. Evaluar última lectura (Motor de Reglas)
    ultima_lectura = lecturas[-1].valor
    if ultima_lectura > 20.0:
        nivel = "PELIGRO"
    elif ultima_lectura > 10.0:
        nivel = "ALERTA"
    else:
        nivel = "NORMAL"
    return {"id": id, "valor": ultima_lectura, "nivel": nivel}

