from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import TelemetryIn, TelemetryInList
from .schemas import Telemetry
from ..alert.schemas import Alert
from sqlalchemy.orm import Session
from ..database import redis_client, hash_password
from ..vehicle.schemas import Vehicle

router = APIRouter()

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
    
def validateRequest(telemetry: TelemetryIn, db: Session):
    password = db.query(Vehicle.password).filter(Vehicle.vin).first()
    return (hash_password(telemetry.password) == password)

def handleDups(telemetry: TelemetryIn, db: Session):
    db_tel: Telemetry = db.query(Telemetry.timestamp).filter(Telemetry.timestamp == telemetry.timestamp and Telemetry.vin == telemetry.vin).first()
    if db_tel:
        db_tel.latitude = telemetry.latitude
        db_tel.longitude = telemetry.longitude
        db_tel.speed = telemetry.speed
        db_tel.engineStatus = telemetry.engineStatus
        db_tel.fuel = telemetry.fuel
        db_tel.odometerReading = telemetry.odometerReading
        db_tel.diagnosticCode = telemetry.diagnosticCode
        return True
    return False

def handle_telemetry(telemetry, db: Session):
    if not validateRequest(telemetry, db):
        raise HTTPException(status_code=401, detail="Wrong Password for Vehicle")
    
    if handleDups(telemetry, db):
        return
    
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
        diagnosticCode = telemetry.diagnosticCode,
        timestamp = telemetry.timestamp
    )

    fleet_id = db.query(Vehicle.fleetId).filter(Vehicle.vin == telemetry.vin).first()[0]
    redis_client.set(f"{fleet_id}avgFuel", -1)
    redis_client.set(f"{fleet_id}distTot", -1)
    
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    
@router.post("/batch")
async def create_telemetry(telemetry: TelemetryInList):
    db = SessionLocal()
    try:
        processed_vins = set()
        for tel in telemetry:
            handle_telemetry(tel, db)
            processed_vins.add(tel.vin)
        
        return {"success": True}
    finally:
        db.close()

@router.post("/")
async def create_telemetry(telemetry: TelemetryIn):
    db = SessionLocal()
    try:
        handle_telemetry(telemetry, db)
        return {"success": True}
    finally:
        db.close()

@router.get("/all")
async def get_telemetry():
    db = SessionLocal()
    try:
        db_telemetry = db.query(Telemetry).all()
        return db_telemetry
    finally:
        db.close()

@router.get("/{telemetry_id}")
async def get_telemetry(telemetry_id: int):
    db = SessionLocal()
    try:
        db_telemetry = db.query(Telemetry).filter(Telemetry.telemetryId == telemetry_id).first()
        if not db_telemetry:
            raise HTTPException(status_code=404, detail="Telemetry Not Found")
        return db_telemetry
    finally:
        db.close()