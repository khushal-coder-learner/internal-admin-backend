from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class MultiUserResponse(BaseModel):
    items: list[UserResponse]
    total: int

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole  # "admin" or "staff"


class UserUpdate(BaseModel):
    role: Optional[UserRole] = None

class UserStatusUpdate(BaseModel):
    is_active: bool