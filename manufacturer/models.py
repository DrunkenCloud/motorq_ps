from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Manufacturer(Base):
    __tablename__ = "manufacturers"
    manufacturerId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    manufacturerName = Column(String)