from sqlalchemy import Column, Integer, ForeignKey, Enum, Float, DateTime
from sqlalchemy.sql import func
from .models import engineStatuses
from ..database import Base

class Telemetry(Base):
    __tablename__ = "telemetries"
    telemetryId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    vin = Column(Integer, ForeignKey("vehicles.vin"))
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    odometerReading = Column(Integer)
    fuel = Column(Float)
    engineStatus = Column(Enum(engineStatuses))
    diagnosticCode = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())