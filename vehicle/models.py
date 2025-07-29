from enum import Enum
from pydantic import BaseModel

class regStatuses(str, Enum):
    active = "active"
    maintenance = "maintenance"
    decommisioned = "decommisioned"

class VehicleIn(BaseModel):
    vin: int
    modelId: int
    fleetId: int
    operatorId: int
    ownerId: int
    regStatus: regStatuses
    password: str