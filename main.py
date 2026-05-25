from fastapi import FastAPI, HTTPException, Depends,status,Request

from sqlalchemy.orm import Session
from src.Services.ChatService import chat
from src.config.db import get_db, User
from src.schemas.User import UserCreate, UserResponse

from src.schemas.question_schemas import QuestionResponse,SubmitAnswer,ResultResponse,QuizCreate
from src.Analysis.Quiz import get_quiz
import json

from src.config.db import (
    QuizModel,
    QuestionModel
)



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
    quiz_data: QuizCreate,
    db: Session = Depends(get_db)
):
    try:

        query = f"""
        Create a 10 highly precise quiz based on:

        Topic: {quiz_data.topic}
        Difficulty: {quiz_data.difficulty}

        IMPORTANT:
        - Return ONLY valid JSON
        - No markdown
        - No explanation
        - No extra text

        JSON FORMAT:
        [
          {{
            "question": "Question here",
            "options": {{
              "A": "Option A",
              "B": "Option B",
              "C": "Option C",
              "D": "Option D"
            }},
            "correct_answer": "A"
          }}
        ]
        """

        content = get_quiz(query)

        quiz_json = json.loads(content)

        new_quiz = QuizModel(
            user_id=1, 
            topic=quiz_data.topic,
            difficulty=quiz_data.difficulty
        )

        db.add(new_quiz)
        db.commit()
        db.refresh(new_quiz)

        for item in quiz_json:

            question = QuestionModel(
                quiz_id=new_quiz.id,

                question_text=item["question"],

                option_a=item["options"]["A"],
                option_b=item["options"]["B"],
                option_c=item["options"]["C"],
                option_d=item["options"]["D"],

                correct_answer=item["correct_answer"]
            )

            db.add(question)

        db.commit()

        return {
            "quiz_id": new_quiz.id,
            "questions": quiz_json
        }

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail="AI did not return valid JSON"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )