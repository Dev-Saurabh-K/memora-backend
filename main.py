from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy.orm import Session
from src.Services.ChatService import chat
from src.config.db import get_db, User
from src.schemas.User import UserCreate, UserResponse




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