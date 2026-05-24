from fastapi import FastAPI, HTTPException, Depends, status

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from src.Services.ChatService import chat
from src.config.db import get_db, User, Chat, get_chatdb
from src.schemas.User import UserCreate, UserResponse
from src.schemas.Chat import ChatMessage, ChatMessageResponse, RetrieveChatResponse
from src.auth.auth import hash_password, decode_access_token, create_access_token, verify_password
from typing import List


from datetime import datetime



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
    