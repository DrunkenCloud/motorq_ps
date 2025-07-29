from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import FleetIn
from .schemas import Fleet

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
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

@router.get("/{fleet_id}")
async def get_fleet(fleet_id: int):
    db = SessionLocal()
    db_fleet = db.query(Fleet).filter(Fleet.fleetId == fleet_id).first()
    if not db_fleet:
        raise HTTPException(status_code=404, detail="Fleet not found")
    return db_fleet