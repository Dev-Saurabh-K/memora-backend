from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    emailid: str
    password: str
    studying_at: str

class UserResponse(BaseModel):
    id: int
    username: str
    emailid: str
    password: str
    studying_at: str
    model_config = {
        "from_attributes": True
    }

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    emailid: Optional[str] = None
    password: Optional[str] = None
    studying_at: Optional[str] = None



    # class Config:
    #     from_attributes = True


