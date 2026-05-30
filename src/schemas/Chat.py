from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatMessage(BaseModel):
    user_id: int
    message: str
    topic_id : int
    # created_at


class ChatMessageResponse(BaseModel):
    user_id: int
    message: str
    topic_id: int
    # created_at

class RetrieveChatResponse(BaseModel):
    user_id: int
    usermessage: Optional[str] = None
    aimessage: Optional[str] = None 
    # created_at: datetime

    class Config:
        from_attributes = True