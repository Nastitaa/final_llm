from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserPublic(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime
    model_config = {"from_attributes": True}