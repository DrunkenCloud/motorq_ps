from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Model(Base):
    __tablename__ = "models"
    modelId = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    modelName = Column(String)
    manufactererId = Column(Integer, ForeignKey("manufacturers.manufacturerId"))