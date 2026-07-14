from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class CompetitorBase(BaseModel):
    name: str
    website_url: HttpUrl
    apify_actor_id: str

class CompetitorCreate(CompetitorBase):
    client_id: int

class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    apify_actor_id: Optional[str] = None
    client_id: Optional[int] = None

class CompetitorResponse(CompetitorBase):
    id: int
    client_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
