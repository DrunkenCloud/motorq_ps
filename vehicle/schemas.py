from sqlalchemy import Column, Integer, ForeignKey, Enum, String
from .models import regStatuses
from ..database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    vin = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    modelId = Column(Integer, index=True)
    fleetId = Column(Integer, ForeignKey("fleets.fleetId"))
    operatorId = Column(Integer, ForeignKey("humans.humanId"))
    ownerId = Column(Integer, ForeignKey("humans.humanId"))
    regStatus = Column(Enum(regStatuses))
    password = Column(String)