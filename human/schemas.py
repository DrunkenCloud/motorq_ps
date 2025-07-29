from sqlalchemy import Column, Integer, String
from ..database import Base

class Human(Base):
    __tablename__ = "humans"
    humanId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    humanName = Column(String)