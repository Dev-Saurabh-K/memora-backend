from fastapi import FastAPI, HTTPException, Depends,status,Request, status, UploadFile, File, Query, APIRouter

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from fastapi.concurrency import run_in_threadpool

from sqlalchemy import func
from sqlalchemy.orm import Session
# from src.Services.ChatService import chat
from src.config.db import get_db, User, Chat, Topics, SubNotes, QuizQuestion, QuizPerformance
from src.schemas.User import UserCreate, UserResponse, UserUpdateRequest
from src.schemas.Chat import ChatMessage, ChatMessageResponse, RetrieveChatResponse
from src.schemas.Topic import AskTopic, TopicResponse, HistoryResponse
from src.schemas.Notes import NotesRequest, NotesResponse, SubnotesRequest
from src.schemas.Quiz import QuizSubmitRequest, QuizSubmitResponse, QuizPerformanceResponse
from src.Services.microtasks import extractTextFromPDF
from src.Services.GeneratePlan import generateTopic
from src.Services.NotesGenerator import notes_generator
from src.Services.SubNotesGenerator import generate_sub_notes
from src.Services.GetImage import get_image_url
from src.Services.quiz import generateQuiz
from src.auth.auth import hash_password, decode_access_token, create_access_token, verify_password
from src.Services.imagekitsetup import imagekit
from src.Services.EmbeddingServiceStorage import storeTextInVectorStore, retrieveAnswersFromTexts
from typing import List
import json
import time
import json

app = FastAPI()


# for developement
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # For development
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],

# )

# for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "https://private-sigma-mauve.vercel.app",
        "https://hacksphere-i01cihcir-saurabh-kumars-projects-ee8f1350.vercel.app/",
        "https://hacksphere1.vercel.app",
    ],
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

@app.get("/")
def test_api():
    return {
        "status":"working"
    }


# example protected route
@app.get("/protected/user/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

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
def get_topic(history_group: int, db:Session=Depends(get_db), current_user: User = Depends(get_current_user)):
    all_topics = db.query(Topics).filter(
        Topics.user_id == current_user.id,
        Topics.history_group == history_group).all()
    return all_topics

@app.post("/api/generate/notes", response_model=NotesResponse)     
async def get_notes( topic:NotesRequest , db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):

    topic_to_update = db.query(Topics).filter(
        Topics.user_id == current_user.id,
        Topics.id==topic.topic_id,
        ).first()
    
    if(topic_to_update.topic_notes==None):

    
        # data = notes_generator(topic=topic, subject=subject)
        data = await run_in_threadpool(notes_generator, topic_to_update.topic_text, topic_to_update.subject)
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

@app.get("/api/retrieve/notes")
def retrieve_notes(topic_id:int, db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):
    data = db.query(Topics).filter(
        Topics.user_id == current_user.id,
        Topics.id == topic_id,
    ).first()
    

    return data

@app.post("/api/generate/subnotes")
async def get_subnotes(req: SubnotesRequest, db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):
    data = db.query(SubNotes).filter(
        SubNotes.topic_id
    )
    data = await run_in_threadpool(generate_sub_notes, req.keyword, req.context)
    return data

@app.get("/api/generate/image")
def get_image(topic: str):
    url=get_image_url(topic)
    return (
        {
            "imageurl":url
        }
    )

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
def retrive_message(topic_id:int, db: Session = Depends(get_db), current_user : User = Depends(get_current_user)):

    
    all_chats = db.query(Chat).filter(
        Chat.user_id == current_user.id,
        Chat.topic_id == topic_id
        ).all()
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
    
@app.get("/api/notes/quiz", response_model=List[QuizSubmitResponse])
async def generate_quiz(topic_id:int, db:Session = Depends(get_db), current_user:User = Depends(get_current_user)):

    #check esisting question
    check_existing_question = db.query(QuizQuestion).filter(QuizQuestion.user_id == current_user.id, QuizQuestion.topic_id == topic_id).all()
    if check_existing_question:
        return check_existing_question
    
    topic_details = db.query(Topics).filter(
        Topics.user_id == current_user.id,
        Topics.id == topic_id
        ).first()
    
    quiz = await run_in_threadpool(generateQuiz, topic_details.topic_notes, topic_details.subject, current_user.studying_at)

    batch_id = int(time.time())
    questions_to_insert = []

    for question in quiz.questions:
        row_data = {
            "user_id":current_user.id,
            "topic_id":topic_id,
            "batch_id":batch_id,
            "question":question.question,
            "answer":question.correct_answer,
            "options":question.options
        }
        questions_to_insert.append(row_data)

    db.bulk_insert_mappings(QuizQuestion, questions_to_insert)
    db.commit()
    saved_questions = db.query(QuizQuestion).filter(QuizQuestion.user_id == current_user.id, QuizQuestion.topic_id == topic_id).all()
    return saved_questions
    
@app.post("/api/notes/quiz/submit", response_model=List[QuizSubmitResponse])
def submit_quiz(request: QuizSubmitRequest, db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    question_db = db.query(QuizQuestion).filter(QuizQuestion.batch_id == request.batch_id, QuizQuestion.user_id == current_user.id).all()

    for index, question in enumerate(question_db):
        question.chosen_answer = request.chosen_options[index]

    db.commit()
    return db.query(QuizQuestion).filter(QuizQuestion.batch_id == request.batch_id).all()


@app.get("/api/quiz/score",response_model=QuizPerformanceResponse)
def get_score(topic_id: int, db:Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    score = 0
    quiz_data = db.query(QuizQuestion).filter(QuizQuestion.user_id==current_user.id, QuizQuestion.topic_id==topic_id).all()

    if not quiz_data:
        raise HTTPException(status_code=404,detail="Quiz question not generated yet!")

    attended = False

    for question in quiz_data:
        if question.chosen_answer == question.answer:
            score += 1

        if question.chosen_answer is not None:
            attended = True
    

    subject = db.query(Topics).filter(Topics.id==topic_id, Topics.user_id==current_user.id).first().subject
    existing_data = db.query(QuizPerformance).filter(
    QuizPerformance.topic_id == topic_id,
    QuizPerformance.user_id == current_user.id,
    ).first()
    if existing_data:
        existing_data.attended=attended
        existing_data.score=score
        db.commit()
        return existing_data
    


    data = QuizPerformance(user_id=current_user.id, topic_id=quiz_data[0].topic_id, score=score, subject=subject, attended=attended)

    db.add(data)
    db.commit()
    db.refresh(data)

    return data

    # return response
    # return score
    # return quiz_data

@app.get("/api/analytics/subjectscore")
def get_subjectScore_graph_data(db:Session=Depends(get_db), current_user: User= Depends(get_current_user)):
    quiz = db.query(QuizPerformance).filter(QuizPerformance.user_id==current_user.id, QuizPerformance.attended==True).all()
    subjects = db.query(Topics.subject).distinct().all()
    print(subjects)
    return [row[0] for row in subjects]

