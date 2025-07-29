from pydantic import BaseModel

class FleetIn(BaseModel):
    name: str
    manufacturerId: int