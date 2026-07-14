from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClientBase(BaseModel):
    name: str
    email_address: EmailStr
    is_active: bool = True

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email_address: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class ClientResponse(ClientBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
