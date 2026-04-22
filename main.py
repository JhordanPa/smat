from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware

# =====================================================
# CRITICAL: CREACIÓN DE LA BASE DE DATOS Y TABLAS
# Esta línea busca el archivo 'smat.db' y crea las tablas
# =====================================================
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SMAT - Sistema de Monitoreo de Alerta Temprana",
    description="""
    API robusta para la gestión y monitoreo de desastres naturales.
    Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.
    **Entidades principales:**
    * **Estaciones:** Puntos de monitoreo físico.
    * **Lecturas:** Datos capturados por sensores.
    * **Riesgos:** Análisis de criticidad basado en umbrales.
    """,
    version="1.0.0",
    terms_of_service="http://unmsm.edu.pe/terms/",
    contact={
        "name": "Soporte Técnico SMAT - FISI",
        "url": "http://fisi.unmsm.edu.pe",
        "email": "desarrollo.smat@unmsm.edu.pe",
    },
    license_info={
    "name": "Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Configuración de orígenes permitidos
origins = ["*"] # En producción, especificar dominios reales
app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)



# ENDPOINTS REFACTORIZADOS
@app.post(
    "/estaciones/",
    status_code=201,
    tags=["Gestión de Infraestructura"],
    summary="Registrar una nueva estación de monitoreo",
    description="Inserta una estación física (ej. río, volcán, zona sísmica) en la base de datos relacional."
)
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(get_db)):
    # Convertimos el esquema de Pydantic a Modelo de SQLAlchemy
    nueva_estacion = models.EstacionDB(id=estacion.id, nombre=estacion.nombre, ubicacion=estacion.ubicacion)
    
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    
    return {"msj": "Estación guardada en DB", "data": nueva_estacion}

@app.post(
    "/lecturas/",
    status_code=201,
    tags=["Telemetría de Sensores"],
    summary="Recibir datos de telemetría",
    description="Recibe el valor capturado por un sensor y lo vincula a una estación existente mediante su ID."
)
def registrar_lectura(lectura: schemas.LecturaCreate, db: Session = Depends(get_db)):
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

@app.get(
    "/estaciones/{id}/historial",
    tags=["Reportes Historicos"],
    summary="Conteo y promedio de lecturas por estación",
    description="Devuelve el número total de lecturas registradas y el valor promedio para una estación específica.",
    responses={404: {"description": "No se encontraron lecturas para esta estación"}}
)
def obtener_historial_estacion(id: int, db: Session = Depends(get_db)):
    # El recepcionista va al archivero y busca solo las lecturas que coincidan con el ID
    historial = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).all()
    
    # Si la lista está vacía, avisamos que no hay datos
    if not historial:
        raise HTTPException(status_code=404, detail="No se encontraron lecturas para esta estación")
        
    return historial

@app.get(
    "/estaciones/{id}/riesgo",
    tags=["Análisis de Riesgo"],
    summary="Evaluar nivel de peligro actual",
    description="Analiza la última lectura recibida de una estación y determina si el estado es NORMAL, ALERTA o PELIGRO."
)
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
    # 1. Validar si la estación existe en el archivero
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    # 2. Buscar la ÚLTIMA lectura registrada para esa estación
    # Usamos .order_by para que nos traiga la más reciente primero
    ultima_lectura = db.query(models.LecturaDB).filter(
        models.LecturaDB.estacion_id == id
    ).order_by(models.LecturaDB.id.desc()).first()

    if not ultima_lectura:
        return {"id": id, "nivel": "SIN DATOS", "valor": 0}

    # 3. Motor de Reglas (Umbrales del laboratorio)
    valor = ultima_lectura.valor
    if valor > 20.0:
        nivel = "PELIGRO"
    elif valor > 10.0:
        nivel = "ALERTA"
    else:
        nivel = "NORMAL"

    return {"id": id, "valor": valor, "nivel": nivel}

@app.get(
    "/reportes/criticos",
    tags=["Auditoria"],
    summary="Obtener reporte de lecturas críticas",
    description="Genera un listado de todas las lecturas en el ecosistema que representan un peligro. Permite modificar el parámetro opcional 'umbral' para definir a partir de qué valor numérico se considera crítico (el valor por defecto es 20.0)."
)
def obtener_reportes_criticos(umbral: float = 20.0, db: Session = Depends(get_db)):
    # El archivero busca todas las lecturas que superen el número del umbral
    lecturas_criticas = db.query(models.LecturaDB).filter(models.LecturaDB.valor > umbral).all()
    
    return {
        "umbral_aplicado": umbral, 
        "total_alertas": len(lecturas_criticas), 
        "datos_criticos": lecturas_criticas
    }
    
@app.get(
    "/estaciones/stats",
    tags=["Resumen Ejecutivo"],
    summary="Estadísticas generales del ecosistema SMAT",
    description="Proporciona un resumen ejecutivo. Calcula automáticamente el total de estaciones registradas, el volumen de telemetría procesada y el promedio global de todos los sensores."
)
def obtener_estadisticas(db: Session = Depends(get_db)):
    # 1. Contamos cuántas estaciones existen en total
    total_estaciones = db.query(models.EstacionDB).count()
    
    # 2. Traemos todas las lecturas para sacar promedios
    lecturas = db.query(models.LecturaDB).all()
    total_lecturas = len(lecturas)
    
    promedio_global = 0.0
    
    # 3. Matemática básica: si hay lecturas, sumamos todo y dividimos
    if total_lecturas > 0:
        suma_valores = sum(l.valor for l in lecturas)
        promedio_global = suma_valores / total_lecturas
        
    return {
        "estado_sistema": "Operativo",
        "total_estaciones_activas": total_estaciones,
        "total_lecturas_procesadas": total_lecturas,
        "promedio_global_sensores": round(promedio_global, 2)
    }
