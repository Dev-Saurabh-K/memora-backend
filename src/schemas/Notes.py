from pydantic import BaseModel
from typing import Dict, Any, List

class NotesRequest(BaseModel):
    topic_id: int


class NotesResponse(BaseModel):
    id:int
    user_id: int
    history_group: int
    topic_text: str
    keywords: List[str]
    collection: str
    topic_notes:str
    subject:str

class SubnotesRequest(BaseModel):
    keyword: str
    context: str