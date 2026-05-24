from pydantic import BaseModel
from datetime import datetime

class ChatMessage(BaseModel):
    user_id: int
    message: str
    # created_at


class ChatMessageResponse(BaseModel):
    user_id: int
    message: str
    status: str
    # created_at

class RetrieveChatResponse(BaseModel):
    user_id: int
    usermessage: str
    aimessage: str
    created_at: datetime

    class Config:
        from_attributes = True