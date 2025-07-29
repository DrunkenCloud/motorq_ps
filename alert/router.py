from fastapi import APIRouter, HTTPException
from ..database import SessionLocal
from .models import AlertIn
from .schemas import Alert

router = APIRouter()

@router.post("/")
async def create_alert(alert: AlertIn):
    db = SessionLocal()
    db_alert = Alert(
        vin = alert.vin,
        alertTypeId = alert.alertTypeId
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/all")
async def create_alert():
    db = SessionLocal()
    db_alerts = db.query(Alert).all()
    return db_alerts

@router.get("/{alert_id}")
async def get_alert(alert_id: int):
    db = SessionLocal()
    db_alert = db.query(Alert).filter(Alert.alertId == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert Not Found")
    return db_alert

@router.put("/{alert_id}")
async def update_alert(alert_id: int, alert: AlertIn):
    db = SessionLocal()
    db_alert = db.query(Alert).filter(Alert.alertId == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert Not Found")
    db_alert.vin = alert.vin
    db_alert.alertTypeId = alert.alertTypeId
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.delete("/{alert_id}")
async def delete_alert(alert_id: int):
    db = SessionLocal()
    db_alert = db.query(Alert).filter(Alert.alertId == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert Not Found")
    db.delete(db_alert)
    db.commit()
    return {"message": "Alert deleted successfully"}