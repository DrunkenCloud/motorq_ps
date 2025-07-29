from pydantic import BaseModel

class AlertIn(BaseModel):
    vin: int
    alertTypeId: int
