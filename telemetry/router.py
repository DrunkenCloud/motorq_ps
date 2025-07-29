from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import TelemetryIn, TelemetryInList
from .schemas import Telemetry
from ..alert.schemas import Alert

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

@router.post("/batch")
async def create_telemetry(telemetry: TelemetryInList):
    db = SessionLocal()
    for tel in telemetry:
        handle_telemetry(tel, db)
    return {"success" : True }

@router.post("/")
async def create_telemetry(telemetry: TelemetryIn):
    db = SessionLocal()
    handle_telemetry(telemetry, db)
    return {"success" : True }

@router.get("/all")
async def get_telemetry():
    db = SessionLocal()
    db_telemetry = db.query(Telemetry).all()
    return db_telemetry

@router.get("/{telemetry_id}")
async def get_telemetry(telemetry_id: int):
    db = SessionLocal()
    db_telemetry = db.query(Telemetry).filter(Telemetry.telemetryId == telemetry_id).first()
    if not db_telemetry:
        raise HTTPException(status_code=404, detail="Telemetry Not Found")
    return db_telemetry