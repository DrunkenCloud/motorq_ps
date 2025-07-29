from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class AlertType(Base):
    __tablename__ = "alertTypes"
    alertTypeId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    alertTitle = Column(String)
    alertDescription = Column(String)