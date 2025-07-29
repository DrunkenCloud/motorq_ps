from pydantic import BaseModel

class ModelIn(BaseModel):
    name: str
    manufacturerId: int

