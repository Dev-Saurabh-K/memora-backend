from fastapi import FastAPI, HTTPException, Depends

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from src.Services.ChatService import chat
from src.config.db import get_db, User, Chat, get_chatdb
from src.schemas.User import UserCreate, UserResponse
from src.schemas.Chat import ChatMessage, ChatMessageResponse, RetrieveChatResponse
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

@app.get("/")
def home():

    query="what is mitochondria? give answer in one line"
    print(chat(query))
    return {"message": "Hello World"}

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
    