import enum
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Enum, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from .manufacturer.router import router as manufacturer_router

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

class Model(Base):
    __tablename__ = "models"
    modelId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    modelName = Column(String)
    manufactererId = Column(Integer, ForeignKey("manufacturers.manufacturerId"))

class Fleet(Base):
    __tablename__ = "fleets"
    fleetId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    fleetName = Column(String)
    manufactererId = Column(Integer, ForeignKey("manufacturers.manufacturerId"))

class Human(Base):
    __tablename__ = "humans"
    humanId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    humanName = Column(String)

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

class AlertType(Base):
    __tablename__ = "alertTypes"
    alertTypeId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    alertTitle = Column(String)
    alertDescription = Column(String)

class Alert(Base):
    __tablename__ = "alerts"
    alertId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    vin = Column(Integer, ForeignKey("vehicles.vin"))
    alertTypeId = Column(Integer, ForeignKey("alertTypes.alertTypeId"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class HumanIn(BaseModel):
    name: str

class ModelIn(BaseModel):
    name: str
    manufacturerId: int

class FleetIn(BaseModel):
    name: str
    manufacturerId: int

class VehicleIn(BaseModel):
    vin: int
    modelId: int
    fleetId: int
    operatorId: int
    ownerId: int
    regStatus: regStatuses

class AlertTypeIn(BaseModel):
    alertTitle: str
    alertDescription: str

class AlertIn(BaseModel):
    vin: int
    alertTypeId: int

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

@app.post("/model")
async def create_model(model: ModelIn):
    db = SessionLocal()
    db_model = db.query(Model).filter(Model.manufactererId == model.manufacturerId and Model.modelName == model.name).first()
    if db_model:
        raise HTTPException(status_code=409, detail="Model Already Exists")
    db_model = Model(
        modelName = model.name,
        manufactererId = model.manufacturerId
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@app.get("/model/{model_id}")
async def get_model(model_id: int):
    db = SessionLocal()
    db_model = db.query(Model).filter(Model.modelId == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    return db_model

@app.post("/fleet")
async def create_fleet(fleet: FleetIn):
    db = SessionLocal()
    db_fleet = db.query(Fleet).filter(Fleet.manufactererId == fleet.manufacturerId and Fleet.fleetName == fleet.name).first()
    if db_fleet:
        raise HTTPException(status_code=409, detail="Fleet Already Exists")
    db_fleet = Fleet(
        fleetName = fleet.name,
        manufactererId = fleet.manufacturerId
    )
    db.add(db_fleet)
    db.commit()
    db.refresh(db_fleet)
    return db_fleet

@app.get("/fleet/{fleet_id}")
async def get_fleet(fleet_id: int):
    db = SessionLocal()
    db_fleet = db.query(Fleet).filter(Fleet.fleetId == fleet_id).first()
    if not db_fleet:
        raise HTTPException(status_code=404, detail="Fleet not found")
    return db_fleet

@app.post("/human")
async def create_human(human: HumanIn):
    db = SessionLocal()
    db_human = Human(
        humanName = human.name
    )
    db.add(db_human)
    db.commit()
    db.refresh(db_human)
    return db_human

@app.get("/human/{human_id}")
async def get_human(human_id: int):
    db = SessionLocal()
    db_human = db.query(Human).filter(Human.humanId == human_id).first()
    if not db_human:
        raise HTTPException(status_code=404, detail="Fleet not found")
    return db_human

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

@app.post("/alertTypes")
async def create_alert_type(alertType: AlertTypeIn):
    db = SessionLocal()
    db_alertType = db.query(AlertType).filter(AlertType.alertTitle == alertType.alertTitle and AlertType.alertDescription == alertType.alertDescription).first()
    if db_alertType:
        raise HTTPException(status_code=409, detail="Alert Type Already Exists")
    db_alertType = AlertType(
        alertTitle = alertType.alertTitle,
        alertDescription = alertType.alertDescription
    )

    db.add(db_alertType)
    db.commit()
    db.refresh(db_alertType)
    return db_alertType

@app.get("/alertTypes/{alert_type_id}")
async def get_alert_type(alert_type_id: int):
    db = SessionLocal()
    db_alertType = db.query(AlertType).filter(AlertType.alertTypeId == alert_type_id).first()
    if not db_alertType:
        raise HTTPException(status_code=404, detail="Alert Type Not Found")
    return db_alertType

@app.post("/alert")
async def create_alert(alert: AlertIn):
    db = SessionLocal()
    db_alert = Alert(
        vin = alert.vin,
        alertTypeId = alert.alertTypeId
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.get("/alerts")
async def create_alert():
    db = SessionLocal()
    db_alerts = db.query(Alert).all()
    return db_alerts

@app.get("/alert/{alert_id}")
async def get_alert(alert_id: int):
    db = SessionLocal()
    db_alert = db.query(Alert).filter(Alert.alertId == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert Not Found")
    return db_alert

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
async def create_telemetry(telemetry: Telemetry | TelemetryInList):
    db = SessionLocal()
    if isinstance(telemetry, List):
        for tel in telemetry:
            handle_telemetry(tel, db)
    else:
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