from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import TelemetryIn, TelemetryInList
from .schemas import Telemetry
from ..alert.schemas import Alert
from sqlalchemy.orm import Session
from ..database import redis_client, verify_password
from ..vehicle.schemas import Vehicle

def is_rate_limited(vin: str) -> bool:
    key = f"rate_limit:{vin}"
    current = redis_client.get(key)

    if current is None:
        redis_client.set(key, 1, ex=60)
        return False
    elif int(current) >= 4:
        return True
    else:
        redis_client.incr(key)
        return False

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
    password = db.query(Vehicle.password).filter(Vehicle.vin).first()[0]
    return verify_password(telemetry.password,password)

def handle_telemetry(telemetry, db: Session):
    if not validateRequest(telemetry, db):
        raise HTTPException(status_code=401, detail="Wrong Password for Vehicle")
    
    if is_rate_limited(telemetry.vin):
        raise HTTPException(status_code=429, detail="Rate limit exceeded: Max 2 requests per minute.")
    
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

@router.put("/{telemetry_id}")
async def update_telemetry(telemetry_id: int, telemetry: TelemetryIn):
    db = SessionLocal()
    try:
        db_telemetry = db.query(Telemetry).filter(Telemetry.telemetryId == telemetry_id).first()
        if not db_telemetry:
            raise HTTPException(status_code=404, detail="Telemetry Not Found")
        
        handle_telemetry(telemetry, db)

        db_telemetry.vin = telemetry.vin
        db_telemetry.latitude = telemetry.latitude
        db_telemetry.longitude = telemetry.longitude
        db_telemetry.speed = telemetry.speed
        db_telemetry.engineStatus = telemetry.engineStatus
        db_telemetry.fuel = telemetry.fuel
        db_telemetry.odometerReading = telemetry.odometerReading
        db_telemetry.diagnosticCode = telemetry.diagnosticCode
        db_telemetry.timestamp = telemetry.timestamp
        
        db.commit()
        db.refresh(db_telemetry)
        return db_telemetry
    finally:
        db.close()

@router.delete("/{telemetry_id}")
async def delete_telemetry(telemetry_id: int):
    db = SessionLocal()
    try:
        db_telemetry = db.query(Telemetry).filter(Telemetry.telemetryId == telemetry_id).first()
        if not db_telemetry:
            raise HTTPException(status_code=404, detail="Telemetry Not Found")
        db.delete(db_telemetry)
        db.commit()
        return {"message": "Telemetry deleted successfully"}
    finally:
        db.close()