from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func
from ..database import Base

class AlertType(Base):
    __tablename__ = "alertTypes"
    alertTypeId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    alertTitle = Column(String)
    alertDescription = Column(String)