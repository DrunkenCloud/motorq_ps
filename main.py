import enum
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Enum, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from .manufacturer.router import router as manufacturer_router
from .model.router import router as model_router
from .fleet.router import router as fleet_router
from .human.router import router as human_router
from .alert.schemas import Alert

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class regStatuses(str, enum.Enum):
    active = "active"
    maintenance = "maintenance"
    decommisioned = "decommisioned"

class engineStatuses(str, enum.Enum):
    on = "on"
    off = "off"
    idle = "idle"

class Vehicle(Base):
    __tablename__ = "vehicles"
    vin = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    modelId = Column(Integer, index=True)
    fleetId = Column(Integer, ForeignKey("fleets.fleetId"))
    operatorId = Column(Integer, ForeignKey("humans.humanId"))
    ownerId = Column(Integer, ForeignKey("humans.humanId"))
    regStatus = Column(Enum(regStatuses))

class Telemetry(Base):
    __tablename__ = "telemetries"
    telemetryId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    vin = Column(Integer, ForeignKey("vehicles.vin"))
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    odometerReading = Column(Integer)
    fuel = Column(Float)
    engineStatus = Column(Enum(engineStatuses))
    diagnosticCode = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class VehicleIn(BaseModel):
    vin: int
    modelId: int
    fleetId: int
    operatorId: int
    ownerId: int
    regStatus: regStatuses
    
class TelemetryIn(BaseModel):
    vin: int
    latitude: float
    longitude: float
    speed: float
    engineStatus: engineStatuses
    fuel: float
    odometerReading: float
    diagnosticCode: int

class TelemetryInList(BaseModel):
    tel: List[TelemetryIn]

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(manufacturer_router, prefix="/manufacturer")
app.include_router(model_router, prefix="/model")
app.include_router(fleet_router, prefix="/fleet")
app.include_router(human_router, prefix="/human")

@app.post("/vehicle")
async def create_vehicle(vehicle: VehicleIn):
    db = SessionLocal()

    db_vehicle = db.query(Vehicle).filter(Vehicle.vin == vehicle.vin).first()
    if db_vehicle:
        raise HTTPException(status_code=409, detail="Vehicle Already Exists")

    db_vehicle = Vehicle(
        vin = vehicle.vin,
        modelId = vehicle.modelId,
        fleetId = vehicle.fleetId,
        operatorId = vehicle.operatorId,
        ownerId = vehicle.ownerId,
        regStatus = vehicle.regStatus,
    )

    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@app.get("/vehicle/{vin}")
async def get_vehicle(vin: int):
    db = SessionLocal()
    db_vehicle = db.query(Vehicle).filter(Vehicle.vin == vin).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle Not Found")
    return db_vehicle

@app.get("/vehicles")
async def get_vehicles():
    db = SessionLocal()
    db_vehicles = db.query(Vehicle).all()
    return db_vehicles

@app.delete("/vehicle/{vin}")
async def delete_vehicle(vin: int):
    db = SessionLocal()
    db_vehicle = db.query(Vehicle).filter(Vehicle.vin == vin).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle Not Found")
    db.delete(db_vehicle)
    db.commit()
    return {"succes": True}

def check_speed_limis(telemtry: TelemetryIn, db):
    if telemtry.speed > 120:
        db_alert = Alert(
            vin = telemtry.vin,
            alertTypeId = 1
        )
        db.add(db_alert)
        db.commit()

def check_fuel(telemtry: TelemetryIn, db):
    if telemtry.fuel < 0.15:
        db_alert = Alert(
            vin = telemtry.vin,
            alertTypeId = 2
        )
        db.add(db_alert)
        db.commit()

def handle_telemetry(telemetry, db):
    check_speed_limis(telemetry, db)
    check_fuel(telemetry, db)

    db_telemetry = Telemetry(
        vin = telemetry.vin,
        latitude = telemetry.latitude,
        longitude = telemetry.longitude,
        speed = telemetry.speed,
        engineStatus = telemetry.engineStatus,
        fuel = telemetry.fuel,
        odometerReading = telemetry.odometerReading,
        diagnosticCode = telemetry.diagnosticCode
    )
    
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)

@app.post("/telemetry")
async def create_telemetry(telemetry: TelemetryInList):
    db = SessionLocal()
    for tel in telemetry:
        handle_telemetry(tel, db)
    return {"success" : True }

@app.post("/telemetry")
async def create_telemetry(telemetry: TelemetryIn):
    db = SessionLocal()
    handle_telemetry(telemetry, db)
    return {"success" : True }

@app.get("/telemetry/{telemetry_id}")
async def get_telemetry(telemetry_id: int):
    db = SessionLocal()
    db_telemetry = db.query(Telemetry).filter(Telemetry.telemetryId == telemetry_id).first()
    if not db_telemetry:
        raise HTTPException(status_code=404, detail="Telemetry Not Found")
    return db_telemetry

@app.get("/telemetries")
async def get_telemetry():
    db = SessionLocal()
    db_telemetry = db.query(Telemetry).all()
    return db_telemetry

@app.get("/allActiveAndInactive")
async def get_all_active_inactive():
    db = SessionLocal()
    active = len(db.query(Telemetry.vin).distinct().filter(Telemetry.engineStatus == engineStatuses.on).all())
    total = len(db.query(Telemetry.vin).distinct().all())
    return {
        "active" : active,
        "inactive": total-active
    }

@app.get("/avgFuelLevels/{fleet_id}")
async def get_avg_fuel_levels(fleet_id: int):
    db = SessionLocal()
    total_fuel: float = 0
    count: int = 0
    for vin in db.query(Vehicle.vin).filter(Vehicle.fleetId == fleet_id).all():
        value = db.query(Telemetry.fuel).distinct().filter(Telemetry.vin == vin[0]).order_by(Telemetry.timestamp.desc()).first()
        total_fuel += value[0]
        count += 1
    return {"avg": total_fuel/count}

@app.get("/total_distance_traveled/{fleet_id}")
async def get_total_distance_traveled(fleet_id: int):
    db = SessionLocal()
    total_distance: float = 0
    for vin in db.query(Vehicle.vin).filter(Vehicle.fleetId == fleet_id).all():
        value = db.query(Telemetry.odometerReading).distinct().filter(Telemetry.vin == vin[0]).order_by(Telemetry.timestamp.desc()).first()
        total_distance += value[0]
    return {"total_distance": total_distance}

@app.get("/alertSummary")
async def get_alert_summary():
    db = SessionLocal()

    summary = {}
    for alert in db.query(Alert).all():
        if alert.alertTypeId not in summary:
            summary[alert.alertTypeId] = 1
        else:
            summary[alert.alertTypeId] += 1
        
    return summary