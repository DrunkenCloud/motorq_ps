from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import HumanIn
from .schemas import Human

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
        raise HTTPException(status_code=404, detail="Human not found")
    return db_human

@router.put("/{human_id}")
async def update_human(human_id: int, human: HumanIn):
    db = SessionLocal()
    db_human = db.query(Human).filter(Human.humanId == human_id).first()
    if not db_human:
        raise HTTPException(status_code=404, detail="Human not found")
    db_human.humanName = human.name
    db.commit()
    db.refresh(db_human)
    return db_human

@router.delete("/{human_id}")
async def delete_human(human_id: int):
    db = SessionLocal()
    db_human = db.query(Human).filter(Human.humanId == human_id).first()
    if not db_human:
        raise HTTPException(status_code=404, detail="Human not found")
    db.delete(db_human)
    db.commit()
    return {"message": "Human deleted successfully"}