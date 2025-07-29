import enum    
from typing import List
from pydantic import BaseModel

class engineStatuses(str, enum.Enum):
    on = "on"
    off = "off"
    idle = "idle"

class TelemetryIn(BaseModel):
    vin: int
    latitude: float
    longitude: float
    speed: float
    engineStatus: engineStatuses
    fuel: float
    odometerReading: float
    diagnosticCode: int

class TelemetryInList(BaseModel):
    tel: List[TelemetryIn]
