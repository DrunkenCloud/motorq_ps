from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import Human
from .schemas import HumanIn

router = APIRouter()

@router.post("/")
async def create_human(human: HumanIn):
    db = SessionLocal()
    db_human = Human(
        humanName = human.name
    )
    db.add(db_human)
    db.commit()
    db.refresh(db_human)
    return db_human

@router.get("/{human_id}")
async def get_human(human_id: int):
    db = SessionLocal()
    db_human = db.query(Human).filter(Human.humanId == human_id).first()
    if not db_human:
        raise HTTPException(status_code=404, detail="Fleet not found")
    return db_human