from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from ..database import Base

class Alert(Base):
    __tablename__ = "alerts"
    alertId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    vin = Column(Integer, ForeignKey("vehicles.vin"))
    alertTypeId = Column(Integer, ForeignKey("alertTypes.alertTypeId"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())