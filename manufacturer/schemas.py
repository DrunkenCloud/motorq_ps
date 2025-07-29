from sqlalchemy import Column, Integer, String
from ..database import Base

class Manufacturer(Base):
    __tablename__ = "manufacturers"
    manufacturerId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    manufacturerName = Column(String)