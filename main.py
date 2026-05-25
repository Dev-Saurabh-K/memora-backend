from fastapi import FastAPI, HTTPException, Depends,status,Request

from sqlalchemy.orm import Session
from src.Services.ChatService import chat
from src.config.db import get_db, User
from src.schemas.User import UserCreate, UserResponse

from src.config import db
from src.schemas.question_schemas import Question,Quiz,QuizCreate
from src.Analysis.Quiz import get_quiz




app = FastAPI()

@app.get("/")
def home():

    query="what is mitochondria? give answer in one line"
    print(chat(query))
    return {"message": "Hello World"}

@app.get("/users/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    return db.query(User).all()

@app.post("/users/quiz_generate")
def quiz(
    topic: str,
    toughness: str,
    quiz_data: QuizCreate,
    db: Session = Depends(get_db)
):
    try:
        query = f"""
        Create a 10 highly precise quiz based on the following parameters:
        Topic: {quiz_data.topic}
        Toughness Level: {quiz_data.difficulty}

        Ensure that the questions legitimately test the criteria of 
        {quiz_data.difficulty} level.

        Each question must target a very specific sub-topic or nuance 
        within the primary theme.

        Provide realistic distractor choices for options.

        Give response in purely JSON format.
        Give correct option in A,B,C & D.
        """

        content = get_quiz(query)

        result = db.QuizModel(
            topic=quiz_data.topic,
            difficulty=quiz_data.difficulty
        )

        db.add(result)
        db.commit()
        db.refresh(result)

        return {
            "quiz": content,
            "saved_data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gemini Generation Failure"
        )