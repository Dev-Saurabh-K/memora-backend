from fastapi import FastAPI, HTTPException, Depends,status,Request, status, UploadFile, File, Query, APIRouter

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from fastapi.concurrency import run_in_threadpool

from sqlalchemy import func
from sqlalchemy.orm import Session
# from src.Services.ChatService import chat
from src.config.db import get_db, User, Chat, Topics, SubNotes
from src.schemas.User import UserCreate, UserResponse, UserUpdateRequest
from src.schemas.Chat import ChatMessage, ChatMessageResponse, RetrieveChatResponse
from src.schemas.Topic import AskTopic, TopicResponse, HistoryResponse
from src.Services.microtasks import extractTextFromPDF
from src.Services.GeneratePlan import generateTopic
from src.Services.NotesGenerator import notes_generator
from src.Services.SubNotesGenerator import generate_sub_notes
from src.Services.GetImage import get_image_url
from src.auth.auth import hash_password, decode_access_token, create_access_token, verify_password
from src.Services.imagekitsetup import imagekit
from src.Services.EmbeddingServiceStorage import storeTextInVectorStore, retrieveAnswersFromTexts
from typing import List
import json
import time


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
        studying_at = user_data.studying_at
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


# @app.put("/api/user/data", response_model=UserResponse)
@app.put("/api/user/data", response_model=UserResponse)
def update_user_data(user_data: UserUpdateRequest, db:Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    db_user=db.query(User).filter(User.id==current_user.id).first()

    corrected_user_data=user_data.model_dump(exclude_unset=True)

    for field, value in corrected_user_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/generate/syllabus")
async def get_syllabus_plan(file:UploadFile = File(...), db: Session= Depends(get_db), current_user: User = Depends(get_current_user)):
    file_bytes = await file.read()

    # plan = generateTopic((extractTextFromPDF(file_bytes)))
    extracted_PDF = await run_in_threadpool(extractTextFromPDF, file_bytes)
    plan = await run_in_threadpool(generateTopic, extracted_PDF)
    
    current_group_id = int(time.time())

    topics_to_insert = []
    for topic in plan.topics:
        # print(topic.title)

        row_data = {
            "user_id":current_user.id,
            "topic_text":topic.title,
            "subject":topic.subject,
            "history_group": current_group_id
            }
        topics_to_insert.append(row_data)

    db.bulk_insert_mappings(Topics, topics_to_insert)
    db.commit()
    # db.refresh(topics_to_insert)

    return plan


# use topic afterwards
@app.post("/api/generate/addtopic" ,response_model=List[TopicResponse])
async def get_topic_plan(topics: AskTopic, db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = await run_in_threadpool(generateTopic,topics.topic)
    current_group_id = int(time.time())
    topics_to_insert = []
    response_topics= []
    for topic in plan.topics:
        # print(topic.title)

        row_data = {
            "user_id":current_user.id,
            "topic_text":topic.title,
            "subject":topic.subject,
            "history_group": current_group_id
            }
        
        response_topics.append(
            TopicResponse(
                index=getattr(topic, 'index', 1),
                title=topic.title,
                subject=topic.subject,
                

            )
        )
        topics_to_insert.append(row_data)
        
    # db.add(History)
    
    db.bulk_insert_mappings(Topics, topics_to_insert)
    db.commit()

    return response_topics

@app.get("/api/get/history", response_model=List[HistoryResponse])
def get_history(db:Session=Depends(get_db), current_user: User = Depends(get_current_user), limit: int = Query(default=3, description="Number of items to return (e.g., 15 or 100)")):
    # history = db.query(Topics).order_by(Topics.history_group.desc()).limit(limit).all()
    # history = db.query(Topics).distinct(Topics.history_group).order_by(Topics.history_group.desc()).limit(limit).all()
    
    subquery = (
    db.query(func.max(Topics.id))
    .filter(Topics.user_id==current_user.id)
    .group_by(Topics.history_group)
    .subquery()
    )

    
    topics = (
        db.query(Topics)
        .filter(Topics.user_id==current_user.id)
        .filter(Topics.id.in_(subquery))
        .order_by(Topics.history_group.desc())
        .limit(limit)
        .all()
    )
    return topics

@app.get("/api/get/topic")
def get_topic(db:Session=Depends(get_db), current_user: User = Depends(get_current_user)):
    all_topics = db.query(Topics).filter(Topics.user_id == current_user.id).all()
    return all_topics



###############################################################################
#must change response and code if face problem
@app.post("/api/generate/notes")     
async def get_notes(topic: str, subject: str, history_group: int, db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):

    topic_to_update = db.query(Topics).filter(
        Topics.user_id == current_user.id,
        Topics.topic_text==topic,
        Topics.subject == subject,
        Topics.history_group == history_group
        ).first()
    
    if(topic_to_update.topic_notes==None):

    
        # data = notes_generator(topic=topic, subject=subject)
        data = await run_in_threadpool(notes_generator, topic, subject)
        obj = json.loads(data)
        # making collection for vector embeddings
        collection_name = f"{current_user.id}_{topic_to_update.id}"
    
        # if topic_to_update == None:
        #     return {"data":None}
        topic_to_update.topic_notes = obj["paragraph"]
        topic_to_update.keywords = obj["keywords"]
        topic_to_update.collection = collection_name
        # print(obj["paragraph"])

        await run_in_threadpool(storeTextInVectorStore,topic_to_update.topic_notes, collection_name)

        db.commit()
        db.refresh(topic_to_update)
    return topic_to_update
################################################################################

@app.post("/api/retrieve/notes")
def retrieve_notes(topic:str, subject: str, history_group: int, db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):
    data = db.query(Topics).filter(
        Topics.user_id == current_user.id,
        Topics.history_group == history_group,
        Topics.subject == subject,
        Topics.topic_text == topic
    ).first()
    

    return data



@app.post("/api/generate/subnotes")
async def get_subnotes(keyword: str, context: str, db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):
    data = db.query(SubNotes).filter(
        SubNotes.topic_id
    )
    data = await run_in_threadpool(generate_sub_notes, keyword, context)
    return data



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

# @app.post("/api/notes/chat/send", response_model=ChatMessageResponse)
@app.post("/api/notes/chat/send", response_model=ChatMessageResponse)
def send_message(query: ChatMessage, db: Session = Depends(get_db) , current_user: User = Depends(get_current_user)):
    """send query"""

    notes = db.query(Topics).filter(
        Topics.user_id == current_user.id,
        Topics.id == query.topic_id
        ).first()
    
    
    if not notes:
        raise HTTPException(
            status_code=404,
            detail="Topic not found."
        )
    
    if not notes.topic_notes:
        raise HTTPException(
            status_code=400,
            detail="Notes not found."
        )
    
    try:
        collection_name = f"{current_user.id}_{query.topic_id}"
        response = retrieveAnswersFromTexts(query.message, collection_name)


        chat = Chat(user_id = current_user.id, topic_id = query.topic_id, usermessage = query.message, modelmessage = response)
        db.add(chat)
        db.commit()
        db.refresh(chat)


        return ChatMessageResponse(
            user_id = current_user.id,
            message = response,
            topic_id = query.topic_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )
        # storeTextInVectorStore(notes.topic_notes,collection_name)


@app.get("/api/chat/retrive", response_model=List[RetrieveChatResponse])
def retrive_message(db: Session = Depends(get_db), current_user : User = Depends(get_current_user)):

    
    all_chats = db.query(Chat).filter(Chat.user_id == current_user.id).all()
    print(all_chats)
    response = [] 


    for chat in all_chats:
        response.append(RetrieveChatResponse(
            user_id = current_user.id,
            usermessage = chat.usermessage,
            aimessage = chat.modelmessage,
            # created_at = datetime(2026, 1, 1, 12, 0)
        ))
    
    return response
    

@app.post("/users/quiz_generate")
def quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
            user_id=current_user.id, 
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