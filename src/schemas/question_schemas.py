from pydantic import BaseModel,ConfigDict,Field
from typing import List

class QuizCreate(BaseModel):
    topic: str
    difficulty: str
 
class SingleAnswerSubmit(BaseModel):
    question_id: int
    user_answer: str  # "A", "B", "C", or "D"

# What React sends to submit the whole quiz
class QuizSubmission(BaseModel):
    user_id: int      # The ID of the logged-in user
    quiz_id: int      # The ID of the active quiz
    answers: List[SingleAnswerSubmit]
 
class ResultResponse(BaseModel):
    quiz_id: int
    correct_count: int
    total: int
    score_percentage: float

