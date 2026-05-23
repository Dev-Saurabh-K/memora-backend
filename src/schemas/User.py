from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    studyingAt: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    password: str
    studyingAt: str

    # class Config:
    #     from_attributes = True


