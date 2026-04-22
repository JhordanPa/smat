from pydantic import BaseModel
from typing import List, Optional

# --- Esquemas para LECTURAS ---
class LecturaBase(BaseModel):
    valor: float
    estacion_id: int

class LecturaCreate(LecturaBase):
    pass  # Se usa para recibir datos nuevos

class Lectura(LecturaBase):
    id: int  # Este ya incluye el ID que le da la base de datos
    
    class Config:
        from_attributes = True

# --- Esquemas para ESTACIONES ---
class EstacionBase(BaseModel):
    nombre: str
    ubicacion: str

class EstacionCreate(EstacionBase):
    id: int  # En este laboratorio, el ID lo enviamos nosotros

class Estacion(EstacionBase):
    id: int
    # Permite mostrar la lista de lecturas cuando consultamos la estación
    lecturas: List[Lectura] = []

    class Config:
        from_attributes = True