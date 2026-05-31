from pydantic import BaseModel

class NotesRequest(BaseModel):
    topic_id: int
    