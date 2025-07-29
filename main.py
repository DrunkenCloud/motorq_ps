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
from .manufacturer.schemas import Manufacturer
from .model.schemas import Model
from .fleet.schemas import Fleet
from .human.schemas import Human
from .alert_type.schemas import AlertType
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import Base, engine, SessionLocal, hash_password
from .database import redis_client

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
    cache = redis_client.get("{fleet_id}avgFuel")
    if cache != -1:
        return cache
    db = SessionLocal()
    total_fuel: float = 0
    count: int = 0
    for vin in db.query(Vehicle.vin).filter(Vehicle.fleetId == fleet_id).all():
        value = db.query(Telemetry.fuel).distinct().filter(Telemetry.vin == vin[0]).order_by(Telemetry.timestamp.desc()).first()
        total_fuel += value[0]
        count += 1
    redis_client.set("{fleet_id}avgFuel", total_fuel/count)
    return {"avg": total_fuel/count}

@app.get("/total_distance_traveled/{fleet_id}")
async def get_total_distance_traveled(fleet_id: int):
    cache = redis_client.get(f"{fleet_id}distTot")
    if cache is not None:
        try:
            return {"total_distance": float(cache)}
        except ValueError:
            pass

    db: Session = SessionLocal()

    vins = db.query(Vehicle.vin).filter(Vehicle.fleetId == fleet_id).all()
    vins = [vin for (vin,) in vins]

    latest_timestamp = (
        db.query(Telemetry.timestamp)
        .filter(Telemetry.vin.in_(vins))
        .order_by(Telemetry.timestamp.desc())
        .first()
    )

    if not latest_timestamp:
        return {"total_distance": 0.0}

    latest_timestamp = latest_timestamp[0]
    cutoff_time = latest_timestamp - timedelta(hours=24)

    total_distance = 0.0

    for vin in vins:
        latest = (
            db.query(Telemetry.odometerReading)
            .filter(Telemetry.vin == vin)
            .order_by(Telemetry.timestamp.desc())
            .first()
        )

        before_24hr = (
            db.query(Telemetry.odometerReading)
            .filter(
                Telemetry.vin == vin,
                Telemetry.timestamp <= cutoff_time
            )
            .order_by(Telemetry.timestamp.desc())
            .first()
        )

        if latest and before_24hr:
            total_distance += latest[0] - before_24hr[0]

    redis_client.set(f"{fleet_id}distTot", total_distance, ex=86400)
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

@app.post("/seed")
async def seed_data():
    db = SessionLocal()
    # Create Manufacturers
    manufacturers = [
        Manufacturer(name="Toyota"),
        Manufacturer(name="Ford"),
        Manufacturer(name="Honda"),
    ]
    db.add_all(manufacturers)
    db.commit()

    # Create Models
    models = [
        Model(name="Camry", manufacturerId=1),
        Model(name="F-150", manufacturerId=2),
        Model(name="Civic", manufacturerId=3),
    ]
    db.add_all(models)
    db.commit()

    # Create Fleets
    fleets = [
        Fleet(name="West Coast Fleet", manufacturerId=1),
        Fleet(name="East Coast Fleet", manufacturerId=2),
    ]
    db.add_all(fleets)
    db.commit()

    # Create Humans
    humans = [
        Human(name="John Doe"),
        Human(name="Jane Smith"),
    ]
    db.add_all(humans)
    db.commit()

    # Create AlertTypes
    alert_types = [
        AlertType(alertTitle="Low Fuel", alertDescription="Fuel level is critically low."),
        AlertType(alertTitle="Engine Overheating", alertDescription="Engine temperature is too high."),
    ]
    db.add_all(alert_types)
    db.commit()

    # Create Vehicles
    vehicles = [
        Vehicle(vin=12345, modelId=1, fleetId=1, operatorId=1, ownerId=2, regStatus="active", password="password123"),
        Vehicle(vin=67890, modelId=2, fleetId=2, operatorId=2, ownerId=1, regStatus="maintenance", password="password456"),
    ]
    db.add_all(vehicles)
    db.commit()

    # Create Telemetry
    telemetry_data = [
        Telemetry(vin=12345, latitude=34.0522, longitude=-118.2437, speed=65, engineStatus="on", fuel=0.25, odometerReading=50000, diagnosticCode=100, timestamp=datetime.utcnow()),
        Telemetry(vin=67890, latitude=40.7128, longitude=-74.0060, speed=0, engineStatus="off", fuel=0.75, odometerReading=120000, diagnosticCode=0, timestamp=datetime.utcnow()),
    ]
    db.add_all(telemetry_data)
    db.commit()

    # Create Alerts
    alerts = [
        Alert(vin=12345, alertTypeId=1),
        Alert(vin=67890, alertTypeId=2),
    ]
    db.add_all(alerts)
    db.commit()

    return {"message": "Database seeded successfully."}
