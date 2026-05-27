from pydantic import BaseModel,ConfigDict,Field
from typing import List

class QuizCreate(BaseModel):
    topic: str
    difficulty: str
 
class SingleAnswerSubmit(BaseModel):
    question_id: int
    user_answer: str 

class QuizSubmission(BaseModel):
    user_id: int   
    quiz_id: int   
    answers: List[SingleAnswerSubmit]
 
class ResultResponse(BaseModel):
    quiz_id: int
    score: int

class Single_subject(BaseModel):
    subject_name:str
    subject_score:int

class Total_subject(BaseModel):
    user_id: int
    chart_data: List[Single_subject]

    
