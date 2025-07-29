from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import AlertTypeIn
from .schemas import AlertType

router = APIRouter()

@router.post("/alertTypes")
async def create_alert_type(alertType: AlertTypeIn):
    db = SessionLocal()
    db_alertType = db.query(AlertType).filter(AlertType.alertTitle == alertType.alertTitle and AlertType.alertDescription == alertType.alertDescription).first()
    if db_alertType:
        raise HTTPException(status_code=409, detail="Alert Type Already Exists")
    db_alertType = AlertType(
        alertTitle = alertType.alertTitle,
        alertDescription = alertType.alertDescription
    )

    db.add(db_alertType)
    db.commit()
    db.refresh(db_alertType)
    return db_alertType

@router.get("/alertTypes/{alert_type_id}")
async def get_alert_type(alert_type_id: int):
    db = SessionLocal()
    db_alertType = db.query(AlertType).filter(AlertType.alertTypeId == alert_type_id).first()
    if not db_alertType:
        raise HTTPException(status_code=404, detail="Alert Type Not Found")
    return db_alertType

@router.put("/alertTypes/{alert_type_id}")
async def update_alert_type(alert_type_id: int, alertType: AlertTypeIn):
    db = SessionLocal()
    db_alertType = db.query(AlertType).filter(AlertType.alertTypeId == alert_type_id).first()
    if not db_alertType:
        raise HTTPException(status_code=404, detail="Alert Type Not Found")
    db_alertType.alertTitle = alertType.alertTitle
    db_alertType.alertDescription = alertType.alertDescription
    db.commit()
    db.refresh(db_alertType)
    return db_alertType

@router.delete("/alertTypes/{alert_type_id}")
async def delete_alert_type(alert_type_id: int):
    db = SessionLocal()
    db_alertType = db.query(AlertType).filter(AlertType.alertTypeId == alert_type_id).first()
    if not db_alertType:
        raise HTTPException(status_code=404, detail="Alert Type Not Found")
    db.delete(db_alertType)
    db.commit()
    return {"message": "Alert Type deleted successfully"}