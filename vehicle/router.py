from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import VehicleIn, VehicleOut
from .schemas import Vehicle
from ..database import hash_password

router = APIRouter()

@router.post("/")
async def create_vehicle(vehicle: VehicleIn) -> VehicleOut:
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
        password = hash_password(vehicle.password)
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
    return {"success": True}

@router.put("/{vin}")
async def update_vehicle(vin: int, vehicle: VehicleIn):
    db = SessionLocal()
    db_vehicle = db.query(Vehicle).filter(Vehicle.vin == vin).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle Not Found")
    
    db_vehicle.modelId = vehicle.modelId
    db_vehicle.fleetId = vehicle.fleetId
    db_vehicle.operatorId = vehicle.operatorId
    db_vehicle.ownerId = vehicle.ownerId
    db_vehicle.regStatus = vehicle.regStatus
    if vehicle.password:
        db_vehicle.password = hash_password(vehicle.password)
    
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

