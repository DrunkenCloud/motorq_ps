from sqlalchemy import Column, Integer, String, ForeignKey
from ..database import Base

class Fleet(Base):
    __tablename__ = "fleets"
    fleetId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    fleetName = Column(String)
    manufactererId = Column(Integer, ForeignKey("manufacturers.manufacturerId"))