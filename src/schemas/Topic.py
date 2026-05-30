from pydantic import BaseModel
from typing import Dict, Any, Optional


class AskTopic(BaseModel):
    topic: str
    subject: str

class TopicResponse(BaseModel):
    index: int
    title: str
    subject: str

class HistoryResponse(BaseModel):
    id : int
    user_id : int
    history_group : int
    topic_text : str
    topic_notes : Optional[str] = None
    keywords : Optional[Dict[str, Any]] = None
    subject : str

    class Config:
        from_attributes = True