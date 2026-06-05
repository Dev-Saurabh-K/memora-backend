from pydantic import BaseModel
from typing import List, Optional

class QuizSubmitRequest(BaseModel):
    batch_id: int
    chosen_options: List

class QuizSubmitResponse(BaseModel):
    id: int
    user_id: int
    topic_id: int
    batch_id: int
    question: str
    answer: str
    chosen_answer: Optional[str]
    options: List[str]

class QuizPerformanceResponse(BaseModel):
    id: int
    user_id: int
    topic_id: int
    score: int
    subject: str
    attended: bool

class SubjectScore_graph_data(BaseModel):
    user_id: int
    average_score: List[float]
    subject: List[str]