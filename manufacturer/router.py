from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import Manufacturer
from .schemas import ManufactererIn

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
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

@router.get("/{manufacturer_id}")
async def get_manufacturer(manufacturer_id: int):
    db = SessionLocal()
    manufacturer = db.query(Manufacturer).filter(Manufacturer.manufacturerId == manufacturer_id).first()
    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return manufacturer