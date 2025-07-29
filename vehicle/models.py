import enum
from pydantic import BaseModel

class regStatuses(str, enum.Enum):
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