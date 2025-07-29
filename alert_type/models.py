from pydantic import BaseModel

class AlertTypeIn(BaseModel):
    alertTitle: str
    alertDescription: str