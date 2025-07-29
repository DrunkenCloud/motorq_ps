from fastapi import FastAPI
from .manufacturer.router import router as manufacturer_router
from .model.router import router as model_router
from .fleet.router import router as fleet_router
from .human.router import router as human_router
from .alert.router import router as alert_router
from .alert_type.router import router as alert_type_router
from .vehicle.router import router as vehicle_router
from .telemetry.router import router as telemetry_router
from .alert.schemas import Alert
from .telemetry.models import engineStatuses
from .telemetry.schemas import Telemetry
from .vehicle.schemas import Vehicle
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(manufacturer_router, prefix="/manufacturer")
app.include_router(model_router, prefix="/model")
app.include_router(fleet_router, prefix="/fleet")
app.include_router(human_router, prefix="/human")
app.include_router(vehicle_router, prefix="/vehicle")
app.include_router(alert_type_router, prefix="/alert_type")
app.include_router(alert_router, prefix="/alert")
app.include_router(telemetry_router, prefix="/telemetry")

@app.get("/allActiveAndInactive")
async def get_all_active_inactive():
    db = SessionLocal()
    active = db.query(Telemetry.vin).distinct().filter(Telemetry.engineStatus == engineStatuses.on).count()
    total = db.query(Telemetry.vin).distinct().count()
    return {
        "active" : active,
        "inactive": total-active
    }

@app.get("/avgFuelLevels/{fleet_id}")
async def get_avg_fuel_levels(fleet_id: int):
    db = SessionLocal()
    total_fuel: float = 0
    count: int = 0
    for vin in db.query(Vehicle.vin).filter(Vehicle.fleetId == fleet_id).all():
        value = db.query(Telemetry.fuel).distinct().filter(Telemetry.vin == vin[0]).order_by(Telemetry.timestamp.desc()).first()
        total_fuel += value[0]
        count += 1
    return {"avg": total_fuel/count}

@app.get("/total_distance_traveled/{fleet_id}")
async def get_total_distance_traveled(fleet_id: int):
    db: Session = SessionLocal()
    total_distance: float = 0.0
    time_24hrs_ago = datetime.utcnow() - timedelta(hours=24)

    vins = db.query(Vehicle.vin).filter(Vehicle.fleetId == fleet_id).all()
    for (vin,) in vins:
        latest = db.query(Telemetry.odometerReading).filter(
            Telemetry.vin == vin
        ).order_by(Telemetry.timestamp.desc()).first()

        before_24hr = db.query(Telemetry.odometerReading).filter(
            Telemetry.vin == vin,
            Telemetry.timestamp <= time_24hrs_ago
        ).order_by(Telemetry.timestamp.desc()).first()

        if latest and before_24hr:
            total_distance += latest[0] - before_24hr[0]

    return {"total_distance": total_distance}

@app.get("/alertSummary")
async def get_alert_summary():
    db = SessionLocal()

    summary = {}
    for alert in db.query(Alert).all():
        if alert.alertTypeId not in summary:
            summary[alert.alertTypeId] = 1
        else:
            summary[alert.alertTypeId] += 1
        
    return summary