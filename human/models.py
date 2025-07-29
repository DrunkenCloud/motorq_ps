from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Human(Base):
    __tablename__ = "humans"
    humanId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    humanName = Column(String)