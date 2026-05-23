from fastapi import FastAPI
from src.Services.ChatService import chat




app = FastAPI()

@app.get("/")
def home():

    query="what is mitochondria? give answer in one line"
    print(chat(query))
    return {"message": "Hello World"}