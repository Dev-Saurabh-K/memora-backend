from pydantic import BaseModel

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

    # class Config:
    #     from_attributes = True


