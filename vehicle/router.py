from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import VehicleIn
from .schemas import Vehicle

router = APIRouter()

@router.post("/")
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

@router.get("/{vin}")
async def get_vehicle(vin: int):
    db = SessionLocal()
    db_vehicle = db.query(Vehicle).filter(Vehicle.vin == vin).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle Not Found")
    return db_vehicle

@router.get("/")
async def get_vehicles():
    db = SessionLocal()
    db_vehicles = db.query(Vehicle).all()
    return db_vehicles

@router.delete("/{vin}")
async def delete_vehicle(vin: int):
    db = SessionLocal()
    db_vehicle = db.query(Vehicle).filter(Vehicle.vin == vin).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle Not Found")
    db.delete(db_vehicle)
    db.commit()
    return {"succes": True}

