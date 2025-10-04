from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class UserRegistration(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)

    @field_validator("password")
    @classmethod
    def check_password_bytes(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password exceeds 72 bytes when encoded")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
