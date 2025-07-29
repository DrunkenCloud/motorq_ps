import enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Enum, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class regStatuses(str, enum.Enum):
    active = "active"
    maintenance = "maintenance"
    decommisioned = "decommisioned"

class engineStatuses(enum.Enum):
    on = 1
    off = 2
    idle = 3

class Manufacturer(Base):
    __tablename__ = "manufacturers"
    manufacturerId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    manufacturerName = Column(String)

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
    longitute = Column(Float)
    speed = Column(Float)
    odometerReading = Column(Integer)
    fuel = Column(Float)
    engineStatus = Column(Enum(engineStatuses))
    diagnosticCode = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class AlertType(Base):
    __tablename__ = "alertTypes"
    alerTypeId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    alertTitle = Column(String)
    alertDescription = Column(String)

class Alert(Base):
    __tablename__ = "alerts"
    alertId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    vin = Column(Integer, ForeignKey("vehicles.vin"))
    alertTypeId = Column(Integer, ForeignKey("alertTypes.alerTypeId"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class ManufactererIn(BaseModel):
    name: str

class HumanIn(BaseModel):
    name: str

class ModelIn(BaseModel):
    name: str
    manufacturerId: int

class FleetIn(BaseModel):
    name: str
    manufacturerId: int


    # vin = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    # modelId = Column(Integer, index=True)
    # fleetId = Column(Integer, ForeignKey("fleets.fleetId"))
    # operatorId = Column(Integer, ForeignKey("humans.humanId"))
    # ownerId = Column(Integer, ForeignKey("humans.humanId"))
    # regStatus = Column(Enum(regStatuses))

class VehicleIn(BaseModel):
    modelId: int
    fleetId: int
    operatorId: int
    ownerId: int
    regStatus: regStatuses

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/manufacturer")
async def create_manufacturer(manufacturer: ManufactererIn):
    db = SessionLocal()
    db_manu = db.query(Manufacturer).filter(Manufacturer.manufacturerName == manufacturer.name).first()
    if db_manu:
        raise HTTPException(status_code=409, detail="Manufacturer Already Exists")
    db_manu = Manufacturer(manufacturerName=manufacturer.name)
    db.add(db_manu)
    db.commit()
    db.refresh(db_manu)
    return db_manu

@app.get("/manufacturer/{manufacturer_id}")
async def get_manufacturer(manufacturer_id: int):
    db = SessionLocal()
    manufacturer = db.query(Manufacturer).filter(Manufacturer.manufacturerId == manufacturer_id).first()
    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return manufacturer

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