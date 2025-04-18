from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class CustomerSchema(BaseModel):
    uid: UUID
    first_name: str
    second_name: str
    address: str
    permit_number: str

class VehicleSchema(BaseModel):
    uid: UUID
    licence_plate: str
    informations: Optional[str] = None
    km: int = Field(ge=0)
