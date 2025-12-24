from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str  # "admin" or "staff"


class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
