from pydantic import BaseModel,ConfigDict,Field
from typing import List

class QuizCreate(BaseModel):
    topic: str
    difficulty: str
 
class QuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
 
class SubmitAnswer(BaseModel):
    question_id: int
    user_answer: str 
    correct_answer:str
 
class ResultResponse(BaseModel):
    quiz_id: int
    correct_count: int
    total: int
    score_percentage: float

