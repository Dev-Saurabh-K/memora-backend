from fastapi import FastAPI, HTTPException, Depends,status,Request, status, UploadFile, File

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from src.Services.ChatService import chat
from src.config.db import get_db, User, Chat, get_chatdb
from src.schemas.User import UserCreate, UserResponse
from src.schemas.Chat import ChatMessage, ChatMessageResponse, RetrieveChatResponse
from src.Services.microtasks import extractTextFromPDF
from src.Services.GeneratePlan import generateTopic
from src.Services.NotesGenerator import notes_generator
from src.Services.SubNotesGenerator import generate_sub_notes
from src.Services.GetImage import get_image_url
from src.auth.auth import hash_password, decode_access_token, create_access_token, verify_password
from src.Services.imagekitsetup import imagekit
from typing import List


from datetime import datetime
from src.schemas.question_schemas import QuestionResponse,SubmitAnswer,ResultResponse,QuizCreate
from src.Analysis.Quiz import get_quiz
import json

from src.config.db import (
    QuizModel,
    QuestionModel
)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    """Dependency that extracts the user from the incomming JWT token."""
    payload = decode_access_token(token)
    username: str = payload.get("sub")

    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user



# example protected route
@app.get("/protected/user/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user


# @app.get("/")
# def home():

#     query="what is mitochondria? give answer in one line"
#     print(chat(query))
#     return {"message": "Hello World"}



# will work on this in some time
@app.post("/register", response_model=UserResponse)
def register(user_data:UserCreate , db:Session = Depends(get_db)):

    # print(user_data.username)
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed = hash_password(user_data.password)

    # user_dict = user_data.dict()
    # user_dict["password"] = hashed

    # db_user = User(**user_dict)
    db_user = User(
        username = user_data.username,
        password = hashed,
        emailid = user_data.emailid,
        studyingAt = user_data.studyingAt
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    # print(user.password)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Incorrect username or password")

    # create jwt token
    access_token = create_access_token(data={"sub":user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/generate/syllabus")
async def get_syllabus_plan(file:UploadFile = File(...), db: Session= Depends(get_db)):
    file_bytes = await file.read()
    plan = generateTopic((extractTextFromPDF(file_bytes)))
    return {"plan":plan}

@app.post("/api/generate/addtopic")
async def get_topic_plan(topics: str, db:Session= Depends(get_db)):
    plan = generateTopic(topics)
    return {"plan":plan}


###############################################################################
#must change response and code if face problem
@app.post("/api/generate/notes")     
def get_notes(topic: str, subject: str, db:Session= Depends(get_db)):
    return notes_generator(topic=topic, subject=subject)
################################################################################


@app.post("/api/generate/subnotes")
def get_subnotes(keyword: str, context: str):

    return generate_sub_notes(keyword, context)

@app.post("/api/generate/image")
def get_image(topic: str):
    url=get_image_url(topic)
    return (
        {
            "imageurl":url
        }
    )



#upload file
@app.post("/api/upload/file")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):

    file_bytes =await file.read()
    response = imagekit.files.upload(
        file=file_bytes,
        file_name=file.filename
    )

    return response

    




@app.get("/api/users/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    return db.query(User).all()

@app.post("/api/chat/send")
def send_message(query: ChatMessage, chatdb: Session = Depends(get_chatdb)) -> ChatMessageResponse:
    """send query"""


    response = chat(query.message)

    # store in db
    # codes
    # chatdb.add(chat_response)
    new_chat= Chat(
        # user_id = 1,
        usermessage = query.message,
        modelmessage = response
    )

    chatdb.add(new_chat)
    chatdb.commit()

    chatdb.refresh(new_chat)

    chat_response = ChatMessageResponse(
        user_id=1,
        message=response,
        status='sent'
    )

    return chat_response



@app.get("/api/chat/retrive")
def retrive_message(chatdb: Session = Depends(get_chatdb)) -> List[RetrieveChatResponse]:

    
    all_chats = chatdb.query(Chat).all()
    response = [] 


    for chat in all_chats:
        # print(f"User: {chat.usermessage} | AI: {chat.modelmessage}")
        response.append(RetrieveChatResponse(
            user_id = 1,
            usermessage = chat.usermessage,
            aimessage = chat.modelmessage,
            created_at = datetime(2026, 1, 1, 12, 0)
        ))
    
    return response
    

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