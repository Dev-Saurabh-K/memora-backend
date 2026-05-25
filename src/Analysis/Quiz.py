from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_quiz(query:str) -> str:
    model = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite', temperature = 0.1)
    result = model.invoke(query)
    return result.content