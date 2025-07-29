from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import Model
from .schemas import ModelIn

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
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

@router.get("/{model_id}")
async def get_model(model_id: int):
    db = SessionLocal()
    db_model = db.query(Model).filter(Model.modelId == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    return db_model