from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()


def chat(query:str) -> str:
    model = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite', temperature = 0.1)
    messages=[
        SystemMessage(content="You are a helpful AI tutor, answer the question asked in 1 or 2 precise sentence or in a one single paraghraph if instructed or needed"),
        HumanMessage(content=query)
        ]
    result = model.invoke(messages)
    return result.content

