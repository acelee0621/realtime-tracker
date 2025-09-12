# app/schemas/schemas.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class InventoryBase(BaseModel):
    name: str
    quantity: int


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: int


class InventoryResponse(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
