from pydantic import BaseModel


class AskTopic(BaseModel):
    topic: str
    subject: str

class TopicResponse(BaseModel):
    index: int
    title: str
    subject: str